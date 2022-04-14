import argparse
import sys
from numpy import array, isscalar, zeros
import numpy as np
from os import path
from enum import Enum
import awkward as ak
from os.path import splitext
import uproot

from caen_reader import RawDataFile
from waveform import Waveform

N_BOARDS = 2
BOARD_ID_ORDER = [1,2] # board id order in binary file
MAX_N_EVENT = 5000 # Arbiarty large
MAX_BASKET_SIZE = 10 # number of events per TBasket
if MAX_BASKET_SIZE<=10:
    print("Info: write small baskets is not recommended by Jim \
    Pivarski. Code may be slow this way. Rule of thumb: at least \
    100 kb/basket/branch. See: \
    https://github.com/scikit-hep/uproot4/pull/428")


class RunStatus(Enum):
    NORMAL = 0 # all good, keep going
    STOP = 1 # stop the run
    SKIP = 2 # bad, better skip to next

class RawDataRooter():
    """
    Convert BNL raw data collected by V1730 from binary to root
    """
    def __init__(self, args):
        """
        Constructor
        """
        self.args = args # save a copy
        self.start_id = int(args.start_id)
        self.end_id = int(args.end_id)
        self.raw_data_file = RawDataFile(args.if_path)
        if args.output_dir=="":
            self.of_path = args.if_path +'.root'
        else:
            self.of_path = args.output_dir + '/' + args.of

        # counter
        self.n_events = 0 # number of good events
        self.n_triggers = 0 # total num. of triggers

        self.sanity_check()
        self.find_active_ch_names()

    def sanity_check(self):
        '''
        Werid thing may happen. Check.:
        '''
        # Check a few triggers first from binary file
        raw_data_file = RawDataFile(self.args.if_path)
        for i in range(N_BOARDS):
            trigger = raw_data_file.getNextTrigger()
            self.n_triggers += 1
            if i==0:
                t0 = trigger.traces.copy()
            else:
                t1 = trigger.traces
                if t1==t0:
                    sys.exit('Identical traces!')
        raw_data_file.close()
        return None

    def find_active_ch_names(self):
        """
        Find active ch names.
        """
        ch_names = []
        raw_data_file = RawDataFile(self.args.if_path)
        for i in range(N_BOARDS):
            trigger = raw_data_file.getNextTrigger()
            for ch, val in trigger.traces.items():
                ch_names.append(ch)
        self.ch_names = ch_names
        raw_data_file.close()
        return None

    def next(self):
        '''
        Iterates to the next event. One Waveform per events. Each call iterates
        by one event, but one event may contain multiple triggers. getNextTrigger()
        iterates one trigger at a time. Carefully Check the boardId order.

        Returns:
            RunStatus: NORMAL (0), SKIP (1), STOP (2)
        '''
        trigger = self.raw_data_file.getNextTrigger()
        self.n_triggers += 1

        # end of file?
        if trigger is None:
            print("Info: The end of this file is reached. Close.")
            self.raw_data_file.close()
            return RunStatus.STOP

        # only process within [start_id, end_id)
        event_id = trigger.eventCounter
        if event_id<self.start_id or event_id>=self.end_id:
            self.skip_event_id = event_id
            return RunStatus.SKIP

        # If the first boardId is not found in one cycle, stop
        stop_run = False
        if trigger.boardId != BOARD_ID_ORDER[0]:
            stop_run = True # temporially set True
            for i in range(N_BOARDS-1):
                trigger = self.raw_data_file.getNextTrigger()
                self.n_triggers += 1
                if trigger.boardId==BOARD_ID_ORDER[0]:
                    stop_run=False # found it
                    break;
        if stop_run:
            return RunStatus.STOP

        wfm = Waveform(config=None)
        wfm.traces = trigger.traces.copy() # new copy
        wfm.triggerTimeTag = trigger.triggerTimeTag
        wfm.triggerTime = trigger.triggerTime
        wfm.event_id=trigger.eventCounter
        wfm.filePos=trigger.filePos

        for i in range(1, N_BOARDS):
            trigger = self.raw_data_file.getNextTrigger()
            self.n_triggers += 1
            if trigger.boardId != BOARD_ID_ORDER[i]:
                return RunStatus.SKIP
            else:
                wfm.traces.update(trigger.traces)

        self.wfm = wfm # save
        return RunStatus.NORMAL

    def create_output_file(self):
        """
        Create output file
        """
        _, f_ext = splitext(self.of_path)
        if f_ext=='.root':
            self.file = uproot.recreate(self.of_path)

            # dummy channels traces
            ch_names = self.ch_names
            val = np.zeros(2) # dummy
            a = {}
            for ch in ch_names:
                a[ch] = ak.Array([val, []])
            a = ak.zip(a)
            a = ak.values_astype(a, np.uint16)

            # dummy event info
            event = {'id': 'uint32', 'ttt': 'uint32'}

            # make tree
            self.file.mktree("daq", {'adc': a.type, 'event': event },
            initial_basket_capacity=100)
            # self.file['daq'].show()
        else:
            sys.exit('Sorry, requested output file format is not yet implmented.')

    def reset_basket(self):
        self.basket = {}
        for ch in self.ch_names:
            self.basket[ch] = []
        self.event_basket = {'id':[], 'ttt':[]}
        self.basket_size = 0
        return None

    def fill_basket(self):
        a = self.wfm.traces
        for ch, val in a.items():
            self.basket[ch].append(val)
        self.event_basket['id'].append( self.wfm.event_id)
        self.event_basket['ttt'].append( 0 ) #To-Do
        self.basket_size += 1

    def dump_basket(self):
        """
        Write basket to file
        """
        a = ak.zip(self.basket)
        self.file["daq"].extend({"adc": a, 'event': self.event_basket})
        return None

    def close_file(self):
        """
        Close the open data file. Helpful when doing on-the-fly testing
        """
        self.file.close()

def main(argv):
    parser = argparse.ArgumentParser(description='Data Reconstruction Offline Package')
    parser.add_argument('--if_path', type=str, help='Required. full path to the raw data file')
    parser.add_argument('--start_id', type=int, default=0, help='Optional. start process from start_id (default: 0)')
    parser.add_argument('--end_id', type=int, default=MAX_N_EVENT, help='Optional. stop process at end_id (defalt: Arbiarty large)')
    parser.add_argument('--output_dir', type=str, default="", help='Optional. output directory. Default: not specified. If not specified, use input binary file directory.' )
    args = parser.parse_args()

    rooter = RawDataRooter(args)
    rooter.create_output_file()
    rooter.reset_basket()
    for i in range(MAX_N_EVENT):
        status = rooter.next()
        if status==RunStatus.STOP:
            if rooter.basket_size>0:
                rooter.dump_basket()
                print('STOP')
            break
        elif status==RunStatus.SKIP:
            print('SKIP:', i, rooter.skip_event_id, rooter.n_events)
            continue
        else:
            if rooter.basket_size < MAX_BASKET_SIZE:
                rooter.fill_basket()
            else:
                rooter.dump_basket()
                rooter.reset_basket()
            if rooter.n_events % 10==0:
                print('processed %d th events' % rooter.n_events)
            rooter.n_events +=1

    rooter.close_file()


if __name__ == "__main__":
   main(sys.argv[1:])

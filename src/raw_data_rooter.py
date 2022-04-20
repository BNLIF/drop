import argparse
import sys
from numpy import array, isscalar, zeros
import numpy as np
from os import path
from enum import Enum
import awkward as ak
from os.path import splitext
import copy
import uproot

from caen_reader import RawDataFile
from waveform import Waveform

N_BOARDS = 2
BOARD_ID_ORDER = [1,2] # board id order in binary file
MAX_N_EVENT = 999999 # Arbiarty large
MAX_BASKET_SIZE = 1000 # number of events per TBasket
if MAX_BASKET_SIZE<=10:
    print("Info: write small baskets is not recommended by Jim \
    Pivarski. Code may be slow this way. Rule of thumb: at least \
    100 kb/basket/branch. See: \
    https://github.com/scikit-hep/uproot4/pull/428")
INITIAL_BASEKTEL_CAPACITY=1000 # number of basket per file

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
            fname = path.basename( args.if_path)
            self.of_path = args.output_dir + '/' + fname + '.root'

        # useful variables
        self.n_proc_events = 0 # number of good (actually processed) events
        self.proc_event_id = set() # keep a record of processed event id
        self.first_trg_candidate = False
        
        # self.sanity_check()
        self.find_active_ch_names()

    def sanity_check(self):
        '''
        Werid thing may happen. Check.:
        '''
        # Check a few triggers first from binary file
        raw_data_file = RawDataFile(self.args.if_path)
        for i in range(N_BOARDS):
            trg = raw_data_file.getNextTrigger()
            if i==0:
                t0 = trg.traces.copy()
            else:
                t1 = trg.traces
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
            trg = raw_data_file.getNextTrigger()
            for ch, val in trg.traces.items():
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
        if self.first_trg_candidate==False:
            trg = self.raw_data_file.getNextTrigger()
        else:
            trg = self.prev_trg
            
        # end of file?
        if trg is None:
            print("Info: The end of this file is reached. Close.")
            self.raw_data_file.close()
            return RunStatus.STOP

        # only process within [start_id, end_id)
        first_trg_id = trg.eventCounter
        if first_trg_id<self.start_id or first_trg_id>=self.end_id:
            self.skipped_event_id = first_trg_id
            return RunStatus.SKIP

        # the first boardId needs to match BOARD_ID_ORDER[0]. Skip to the next if not.
        if trg.boardId != BOARD_ID_ORDER[0]:
            self.skipped_event_id = first_trg_id
            return RunStatus.SKIP

        # check if the first trigger is duplicated
        if first_trg_id in self.proc_event_id:
            self.skipped_event_id = first_trg_id
            return RunStatus.SKIP
        else:
            self.proc_event_id.add(first_trg_id)
        
        # record the first trigger to waveform
        wfm = Waveform(config=None)
        wfm.traces = trg.traces.copy() # new copy
        wfm.triggerTimeTag = trg.triggerTimeTag
        wfm.triggerTime = trg.triggerTime
        wfm.event_id=first_trg_id
        wfm.filePos=trg.filePos

        # loop over the rest
        for i in range(1, N_BOARDS):
            trg = self.raw_data_file.getNextTrigger()
            if trg.boardId != BOARD_ID_ORDER[i]:
                if trg.boardId==BOARD_ID_ORDER[0]:
                    self.first_trg_candidate=True
                    self.prev_trg = copy.deepcopy(trg)
                else:
                    self.first_trg_candidate=False
                self.skipped_event_id = first_trg_id
                return RunStatus.SKIP
            else:
                wfm.traces.update(trg.traces)
                
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
            initial_basket_capacity=INITIAL_BASEKTEL_CAPACITY)
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
            break
        elif status==RunStatus.SKIP:
            print('SKIP:', i, rooter.skipped_event_id, rooter.n_proc_events, len(rooter.proc_event_id), rooter.proc_event_id)
            continue
        else:
            if rooter.basket_size < MAX_BASKET_SIZE:
                rooter.fill_basket()
            else:
                rooter.dump_basket()
                rooter.reset_basket()
            if rooter.n_proc_events % 100 ==0:
                print('processed %d th events' % rooter.n_proc_events)
            rooter.n_proc_events +=1

    print(rooter.n_proc_events)
    rooter.close_file()


if __name__ == "__main__":
   main(sys.argv[1:])

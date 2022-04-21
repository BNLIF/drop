'''
X. Xiang <xxiang@bnl.gov>

Convert raw data from binary to root format for long term storage. No fancy event reconstruction.

A trigger is a digitizer's data. Map triggers to events by using a event queue. 
An event queue is like a table: row->event_id, col->info

Algotrhim in a nutshell:
0. Create an event queue
1. Read a trigger
2. Check this trigger's event_id in event queue; if not exist, create a new row in the queue. If exist, add to the row.
3. Periodically check if queue has any rows fully filled. If yes, dump the fully filled rows to file.

'''

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


#----------------------------------- 
# Global Parameters are Captialized
#----------------------------------- 
N_BOARDS = 3
MAX_N_TRIGGERS = 999999 # Arbitary large. Larger than n_triggers in raw binary file.
MAX_BASKET_SIZE = 100 # number of events per TBasket in ROOT
INITIAL_BASEKTEL_CAPACITY=1000 # number of basket per file

#if len(BOARD_ID_ORDER) != N_BOARDS:
#    sys.exit("The length of BOARD_ID_ORDER must be N_BOARDS!")
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
            fname = path.basename( args.if_path)
            self.of_path = args.output_dir + '/' + fname + '.root'

        # useful variables
        self.n_trg_read = 0 # number of trigger read from binary (updated in next())
        self.read_event_id = set() # keep a record of event id read in (updated in next())
        self.dumped_event_id = set() # keep a record of event id dumpped
        self.tot_n_evt_proc = 0 # number of good events saved (updated after dump)

        # self.sanity_check()
        self.find_active_ch_names()
        self.reset_event_queue()
        
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
        Find active ch names by reading a few.
        """
        ch_names = set()
        raw_data_file = RawDataFile(self.args.if_path)
        for i in range(20):
            trg = raw_data_file.getNextTrigger()
            for ch, val in trg.traces.items():
                ch_names.add(ch)
        self.ch_names = ch_names
        raw_data_file.close()
        return None

    def next(self):
        '''
        Iterate one trigger at a time. Careful check condition. 
        If all good, fill event_queue.

        Returns:
            RunStatus: NORMAL, SKIP, STOP
        '''
        trg = self.raw_data_file.getNextTrigger()        
        if trg is None: # end of file?
            print("Info: End of file. Close!")
            self.raw_data_file.close()
            return RunStatus.STOP
        
        # only process within [start_id, end_id)
        trg_id = trg.eventCounter
        if trg_id<self.start_id or trg_id>=self.end_id:
            self.skipped_event_id = first_trg_id
            return RunStatus.SKIP
        self.n_trg_read +=1 
        self.read_event_id.add(trg_id)
        
        # duplicated trigger appearing after event dumped to file
        if trg_id in self.dumped_event_id:
            return RunStatus.SKIP
        
        # add to event queue
        status =  self.fill_event_queue(trg)
        return status
        
    def create_output_file(self):
        """
        Create output file
        """
        _, f_ext = splitext(self.of_path)
        if f_ext=='.root':
            
            self.file = uproot.recreate(self.of_path)

            # dummy channels traces
            ch_names = list(self.ch_names)
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
        return None
    
    def reset_event_queue(self):
        """
        Reset the event queue.
        """
        self.event_queue = {}
        return None
        
    def fill_event_queue(self, trg):
        """
        Fill event queue, one trigger at a time.
        """
        boardId = trg.boardId
        trg_id = trg.eventCounter
        if trg_id in self.event_queue:
            for ch, val in trg.traces.items():
                if ch in self.event_queue[trg_id]:
                    # duplicated, send warning
                    print("WARNING: duplicated trigger ???")
                    return RunStatus.SKIP
                else:
                    self.event_queue[trg_id][ch] = val
        else:
            self.event_queue[trg_id] = trg.traces
        # add ttt to the queue
        ttt = trg.triggerTimeTag
        if boardId==1:
            self.event_queue[trg_id]['ttt']=ttt        
        return RunStatus.NORMAL
    
    def get_full_queue_id(self):
        """
        Return a set of event_id in queue that have all info filled
        """        
        all_keys = self.ch_names.copy()
        all_keys.add('ttt')
        full_event_id = set()
        for i, ev in self.event_queue.items():
            if set(ev.keys()) == all_keys:
                full_event_id.add(i)
        return full_event_id
    
    def dump_events(self):
        """
        Dump fully filled events from queue to tree
        """
        # get rows from queue
        i_set = self.get_full_queue_id()
        if len(i_set)==0:
            return None
        # create a basket
        basket = {}
        for ch in self.ch_names:
            basket[ch] = []
        info_basket = {'id': [], 'ttt': []}
        # fill basket
        for i in i_set:
            ev = self.event_queue[i]
            info_basket['id'].append(i)
            info_basket['ttt'].append(ev['ttt'])
            for ch in self.ch_names:
                basket[ch].append(ev[ch])
        a = ak.zip(basket)
        self.file["daq"].extend({"adc": a, 'event': info_basket})
        # remove events from queue
        for i in i_set:
            del self.event_queue[i]
            self.dumped_event_id.add(i) # keep a record of deleted event_id
        self.tot_n_evt_proc = len(self.dumped_event_id)
        return None
                
    def close_file(self):
        """
        Close the open data file. Helpful when doing on-the-fly testing
        """
        self.file.close()
        return None
        
    def print_summary(self):
        print("")
        print("----------------------")
        print("Num. of boards:", N_BOARDS)
        print("Num. of events processed:", self.tot_n_evt_proc)
        print("Num. of triggers read:", self.n_trg_read)
        print("Pass rate:", (self.tot_n_evt_proc*N_BOARDS)/self.n_trg_read)
        return None
    
    def show_progress(self):
        if self.n_trg_read % 100 ==0:
            tot_n_evt_proc = len(self.dumped_event_id)
            print('read %d th trggers,' % self.n_trg_read, " dumped %d events" % tot_n_evt_proc)
        return None
    
def main(argv):
    """
    Main function. Usage:
    python raw_data_rooter.py --help
    """

    parser = argparse.ArgumentParser(description='Data Reconstruction Offline Package')
    parser.add_argument('--if_path', type=str, help='Required. full path to the raw data file')
    parser.add_argument('--start_id', type=int, default=0, help='Optional. start process from start_id (default: 0)')
    parser.add_argument('--end_id', type=int, default=MAX_N_TRIGGERS, help='Optional. stop process at end_id (defalt: Arbiarty large)')
    parser.add_argument('--output_dir', type=str, default="", help='Optional. output directory. Default: not specified. If not specified, use input binary file directory.' )
    args = parser.parse_args()

    rooter = RawDataRooter(args)
    rooter.create_output_file()
    for i in range(MAX_N_TRIGGERS):
        status = rooter.next()
        if status==RunStatus.STOP:
            if len(rooter.event_queue)>0:
                rooter.dump_events()
                print("Leftover in queue (event_id, keys):")
                for i, ev in rooter.event_queue.items():
                    print(i, ev.keys())
            break
        elif status==RunStatus.SKIP:
            tot_n_evt_proc = len(rooter.dumped_event_id)
            print('SKIP:', i, rooter.skipped_event_id, tot_n_evt_proc)
            continue
        else:
            n_queue = len(rooter.event_queue)
            if n_queue >= MAX_BASKET_SIZE:
                rooter.dump_events()
        rooter.show_progress()

    rooter.print_summary()
    rooter.close_file()

if __name__ == "__main__":
   main(sys.argv[1:])

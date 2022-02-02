import argparse
import sys
from numpy import array, isscalar
import numpy as np
from enum import Enum

from yaml_reader import YamlReader
from waveform import Waveform
from caen_reader import RawDataFile
from pulse_finder import PulseFinder
from rq_writer import RQWriter, EventRQBasket

MAX_N_EVENT = 999999999 # Arbiarty large

class RunStatus(Enum):
    NORMAL = 0 # all good, keep going
    STOP = 1 # stop the run
    SKIP = 2 # bad, better skip to next

class RunDROP():
    """
    Main Class. Once per run. Manage all operations.
    """
    def __init__(self, args):
        # args
        self.args = args # save a copy
        self.start_id = int(args.start_id)
        self.end_id = int(args.end_id)
        self.raw_data_file = RawDataFile(args.if_path)
        # config
        self.config  = YamlReader(args.yaml).data
        self.n_boards = int(self.config['n_boards'])
        self.boardId_order=np.array(self.config['boardId_order'], dtype=int)
        # counter
        self.n_events = 0 # number of good events
        self.n_triggers = 0 # total num. of triggers

    def sanity_check(self):
        '''
        Collection of check before running
        '''
        # check ROI in config
        roi_start = np.array(self.config['roi_start'])
        roi_end = np.array(self.config['roi_end'])
        if len(roi_start) != len(roi_end):
            sys.exit('Different list length between roi_start and roi_end.')
        if np.any(roi_end<=roi_start):
            sys.exit('roi_end must be strictly larger than roi_start')

        # Check a few triggers first
        raw_data_file = RawDataFile(self.args.if_path)
        for i in range(self.n_boards):
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

    def next(self):
        '''
        One Waveform per events. Each call iterates by one event.
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
            return RunStatus.SKIP

        # If the first boardId is not found in one cycle, stop
        stop_run = False
        if trigger.boardId != self.boardId_order[0]:
            stop_run = True # temporially set True
            for i in range(self.n_boards-1):
                trigger = self.raw_data_file.getNextTrigger()
                self.n_triggers += 1
                if trigger.boardId==self.boardId_order[0]:
                    stop_run=False # found it
                    break;
        if stop_run:
            return RunStatus.STOP

        wfm = Waveform(self.config)
        wfm.traces = trigger.traces.copy() # new copy
        wfm.triggerTimeTag = trigger.triggerTimeTag
        wfm.triggerTime = trigger.triggerTime
        wfm.event_id=trigger.eventCounter
        wfm.filePos=trigger.filePos

        for i in range(1, self.n_boards):
            trigger = self.raw_data_file.getNextTrigger()
            self.n_triggers += 1
            if trigger.boardId != self.boardId_order[i]:
                return RunStatus.SKIP
            else:
                wfm.traces.update(trigger.traces)

        self.wfm = wfm # save
        return RunStatus.NORMAL

    def display_wfm(self, ch=None):
        self.wfm.display(ch)

    def display_ch_hits(self):
        """here or a separate toolbox class??? """
        pass

def main(argv):
    parser = argparse.ArgumentParser(description='Data Reconstruction Offline Package')
    parser.add_argument('--if_path', type=str, help='Required. full path to the raw data file')
    parser.add_argument('--yaml', type=str, help='Required. path to the yaml config file')
    parser.add_argument('--start_id', type=int, default=0, help='Optional. start process from start_id (default: 0)')
    parser.add_argument('--end_id', type=int, default=MAX_N_EVENT, help='Optional. stop process at end_id (defalt: Arbiarty large)')
    parser.add_argument('--of', type=str, default="", help='Optional. output file including extension (ex. test.root). Full path will be at output_dir/test.root. Default: input file name appended with .root will be used.' )
    args = parser.parse_args()

    # RunDROP is at the top of food-chain
    run = RunDROP(args)

    # create output file to write
    rq_w = RQWriter(run.config, args)
    # create basket to hold rq in memory before writing
    ev_b = EventRQBasket()
    for i in range(MAX_N_EVENT):
        status = run.next()
        if status==RunStatus.STOP:
            if ev_b.size>0:
                rq_w.write_event_rq(ev_b)
            break
        elif status==RunStatus.SKIP:
            continue
        else:
            # RunStatus.NORMAL, proceed reconstruction
            run.n_events +=1

        # do reconstruction
        run.wfm.do_baseline_subtraction()
        run.wfm.sum_channels()
        run.wfm.integrate_waveform()
        pf = PulseFinder(run.config, run.wfm)
        pf.find_pulses()

        if ev_b.size < rq_w.basket_size:
            ev_b.fill(run.wfm, pf)
        else:
            print('hello')
            rq_w.write_event_rq(ev_b)
            ev_b.reset() # empty basket, reset basket size=0

    # write run tree
    rq_w.write_run_rq({
    "n_events": [run.n_events],
    "n_triggers": [run.n_triggers]
    })

    # remeber to close file
    rq_w.close()

if __name__ == "__main__":
   main(sys.argv[1:])

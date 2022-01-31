import argparse
import sys
from numpy import array
import numpy as np
from enum import Enum

from yaml_reader import YamlReader
from waveform import Waveform
from caen_reader import RawDataFile

MAX_N_EVENT = 999999999

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
        self.raw_data_file = RawDataFile(args.raw)
        # config
        self.config  = YamlReader(args.yaml).data
        self.n_boards = int(self.config['n_boards'])
        self.boardId_order=np.array(self.config['boardId_order'], dtype=int)

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
        raw_data_file = RawDataFile(self.args.raw_path)
        for i in range(self.n_boards):
            trigger = raw_data_file.getNextTrigger()
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
    parser.add_argument('--raw', type=str, help='path to the raw data file')
    parser.add_argument('--yaml', type=str, help='path to the yaml config file')
    parser.add_argument('--start_id', type=int, default=0, help='start process from start_id (default: 0)')
    parser.add_argument('--end_id', type=int, default=MAX_N_EVENT, help='stop process at end_id (defalt: Arbiarty large)')
    parser.add_argument('--output', type=str, help='output file (test.root). Full path: output_dir/test.root')
    args = parser.parse_args()

    run = RunDROP(args)
    for i in range(MAX_N_EVENT):
        status = run.next()
        if status==RunStatus.STOP:
            break
        if status==RunStatus.SKIP:
            continue
        if status==RunStatus.NORMAL:
            # do your normal event reconstruction
            pass


if __name__ == "__main__":
   main(sys.argv[1:])

import argparse
import sys
from numpy import array
import numpy as np
from yaml_reader import YamlReader
from waveform import Waveform
from caen_reader import RawDataFile



class RunDROP():
    """
    Main Class. Once per run. Manage all operations.
    """
    def __init__(self, args):
        self.args = args # save a copy
        self.n_events = args.n_events
        self.start_id = args.start_id
        self.raw_data_file = RawDataFile(args.raw)
        self.config  = YamlReader(args.yaml).data
        self.n_boards = int(self.config['n_boards'])
        self.wfm = Waveform(self.config)

        self.t_idx=0 # trigger index
        # self.prev_board_id = 0

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
        wfm = Waveform(self.config)
        trigger = self.raw_data_file.getNextTrigger()
        if trigger is None:
            print("Info: The end of this file is reached. Close.")
            self.raw_data_file.close()
            return False

        # process specific events
        if self.start_id>0 and self.n_events>0:
            start = self.start_id
            end = start + self.n_events
            if trigger.eventCounter<start or trigger.eventCounter>=end:
                return self.next()

        # if trigger.boardId in board_id_list:
        #     return False
        # board_id_list.append(trigger.boardId)

        new_event_flag = self.t_idx % self.n_boards==0
        if new_event_flag:
            wfm.traces = trigger.traces.copy() # new copy
            wfm.triggerTimeTag = trigger.triggerTimeTag
            wfm.triggerTime = trigger.triggerTime
            wfm.event_id=trigger.eventCounter
            wfm.filePos=trigger.filePos
            self.t_idx+=1
        for i in range(self.n_boards-1):
            prev_board_id = trigger.boardId
            trigger = self.raw_data_file.getNextTrigger()
            if prev_board_id==trigger.boardId:
                print('ERROR: repeated boardId')
                return False
            wfm.traces.update(trigger.traces)
            self.t_idx+=1
        self.wfm = wfm # save a copy

        # self.prev_board_id=trigger.boardId
        return True

    def display_wfm(self, ch=None):
        self.wfm.display(ch)

    def display_ch_hits(self):
        """here or a separate toolbox class??? """
        pass

def main(argv):
    parser = argparse.ArgumentParser(description='Data Reconstruction Offline Package')
    parser.add_argument('--raw', type=str, help='path to the raw data file')
    parser.add_argument('--yaml', type=str, help='path to the yaml config file')
    parser.add_argument('--start_id', type=int, default=-1, help='process start with start_id (default: -1)')
    parser.add_argument('--n_events', type=int, default=-1, help='the number of events to process (defalt: -1)')
    args = parser.parse_args()

    run = RunDROP(args)
    while (run.nest()):
        # call algorthim
        pass

if __name__ == "__main__":
   main(sys.argv[1:])

import argparse
import sys
from numpy import array
import numpy as np
from yaml_reader import YamlReader
from waveform import Waveform
from caen_reader import RawDataFile



class RunDROP():

    def __init__(self, args):
        self.args = args # save a copy
        self.n_events = args.n_events
        self.event_id = args.event_id
        self.raw_data_file = RawDataFile(args.raw)
        self.config  = YamlReader(args.yaml).data
        self.n_boards = int(self.config['n_boards'])
        self.wfm = Waveform(self.config)

        self.t_idx=0 # trigger index


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
        if np.any(roi_start-self.config['pre_roi_length']<0):
            sys.exit('poi_start - pre_roi_length is negative')

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

        # process a specific event_id if event_id>0 (defalt: -1)
        if self.event_id>0:
            if trigger.eventCounter!=self.event_id:
                return True

        new_event_flag = self.t_idx % self.n_boards==0
        if new_event_flag:
            wfm.traces = trigger.traces.copy() # new copy
            wfm.triggerTimeTag = trigger.triggerTimeTag
            wfm.triggerTime = trigger.triggerTime
            wfm.eventCounter=trigger.eventCounter
            wfm.filePos=trigger.filePos
            self.t_idx+=1
        for i in range(self.n_boards-1):
            trigger = self.raw_data_file.getNextTrigger()
            wfm.traces.update(trigger.traces)
            self.t_idx+=1
        self.wfm = wfm # save a copy
        return True

    def display_wfm(self, ch=None):
        self.wfm.display(ch)

    def display_ch_hits(self):
        pass

def main(argv):
    parser = argparse.ArgumentParser(description='Data Reconstruction Offline Package')
    parser.add_argument('--raw', type=str, help='path to the raw data file')
    parser.add_argument('--yaml', type=str, help='path to the yaml config file')
    parser.add_argument('--event_id', type=int, default=-1, help='process a single event a specified event_id (default: -1)')
    parser.add_argument('--n_events', type=int, default=-1, help='the number of events to process (defalt: -1)')
    args = parser.parse_args()

    run = RunDROP(args)
    while (run.nest()):
        # call algorthim
        pass

if __name__ == "__main__":
   main(sys.argv[1:])

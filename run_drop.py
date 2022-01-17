import argparse
import sys
from yaml_reader import YamlReader
from yaml_reader import CONFIG
from waveform import Waveform



class RunDROP():

    def __init__(self, args):
        self.args = args
        self.raw_data_file = RawDataFile(args.raw_path)
        self.n_events = args.n_events
        self.event_id = args.event_id
        self.n_boards = int(CONFIG['n_boards'])

        self.t_idx=0 # trigger index
        self.wfm = Waveform()

    def sanity_check(self):
        '''
        Check a few triggers first
        '''
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
        Main Function, reconstruct one event at a time.
        '''
        trigger = self.raw_data_file.getNextTrigger()
        if trigger is None:
            print("Info: The end of this file is reached. Close.")
            self.raw_data_file.close()
            return False

        if self.event_id>0:
            if trigger.eventCounter!=self.event_id:
                return True

        new_event_flag = self.t_idx % n_boards==0
        wfm = Waveform()
        if new_event_flag:
            wfm.traces = trigger.traces.copy()
            wfm.triggerTimeTag = trigger.triggerTimeTag
            wfm.triggerTime = trigger.triggerTime
            wfm.eventCounter=trigger.eventCounter
        while not new_event_flag:
            trigger = self.raw_data_file.getNextTrigger()
            wfm.traces.update(trigger.traces)
        self.wfm = wfm # save a copy
        return True

    def display(self):
        self.wfm.display()

def main(argv):
    parser = argparse.ArgumentParser(description='Data Reconstruction Offline Package')
    parser.add_argument('--raw_path', type=str, help='path to the raw data file')
    parser.add_argument('--yaml', type=str, help='path to the yaml config file')
    parser.add_argument('--event_id', type=int, default=-1, help='process a single event a specified event_id (default: -1)')
    parser.add_argument('--n_events', type=int, default=-1, help='the number of events to process (defalt: -1)')
    args = parser.parse_args()

    # config globally defined in yaml_reader
    CONFIG = YamlReader(args.yaml).data

    run = RunDROP(args)
    while (run.nest()):
        pass

if __name__ == "__main__":
   main(sys.argv[1:])

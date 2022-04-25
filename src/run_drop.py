"""
DROP convert raw waveform to reduced qualities.

Contact:
X. Xiang <xxiang@bnl.gov>
"""
import argparse
import sys
from numpy import array, isscalar
import numpy as np
from enum import Enum
import uproot

from yaml_reader import YamlReader
from waveform import Waveform
from pulse_finder import PulseFinder
from rq_writer import RQWriter

MAX_N_EVENT = 999999999 # Arbiarty large


class RunDROP():
    """
    Main Class. Once per run. Manage all operations.
    """
    def __init__(self, args):
        """
        Args:
            args: return of parser.parse_args(). This is the input arguments
                when you run the program
        """
        # args
        self.args = args # save a copy
        self.start_id = int(args.start_id)
        self.end_id = int(args.end_id)
        self.if_path = args.if_path # save a copy of input file path
        self.load_run_info()

        # config
        self.config  = YamlReader(args.yaml).data
        self.batch_size = int(self.config ['batch_size'])
        self.post_trigger = float(self.config['post_trigger'])
        self.sanity_check()

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
        return None

    def load_run_info(self):
        """
        Load run_info tree, which contains one entry.

        Notes:
            Not yet possible to save str via uproot. Use numbering convension:
            100*boardId + chID,
        """
        f = uproot.open(self.if_path)
        b_names = ['n_boards', 'n_event_proc', 'n_trg_read', 'leftover_event_id', 'active_ch_id']
        a = f['run_info'].arrays(b_names, library='np')
        self.n_boards = a['n_boards'][0]
        self.n_trg_read=a['n_trg_read'][0]
        self.n_event_proc = a['n_event_proc'][0]
        self.leftover_event_id = a['leftover_event_id'][0]
        self.ch_id = sorted(a['active_ch_id'][0])
        self.ch_names = ["adc_b%d_ch%d" % (i // 100, i % 100) for i in self.ch_id]
        return None

    def process_batch(self, batch, writer:RQWriter):
        '''
        Process one batch at a time. Batch size is defined in the yaml file.

        Args:
        - batch: high-level awkward array
        - writer: RQWriter
        '''
        # reset writer
        writer.reset()

        # create waveform, PulseFinder,
        wfm = Waveform(self.config)
        wfm.set_ch_names(self.ch_names)
        wfm.set_n_boards(self.n_boards)

        # create PulseFinder
        pf = PulseFinder(self.config, wfm)

        # loop over events
        for i in range(len(batch)):
            event_id = batch[i].event_id
            event_ttt = batch[i].event_ttt
            if event_id<self.start_id or event_id>=self.end_id:
                continue

            # waveform
            wfm.reset()
            wfm.set_raw_data(batch[i])
            wfm.do_baseline_subtraction()
            wfm.sum_channels()
            wfm.integrate_waveform()
            # pulses finding
            pf.reset()
            pf.wfm = wfm
            pf.find_pulses()
            # fill rq event structure
            writer.fill(wfm, pf)
        writer.dump_event_rq()
        return None


    # def display_wfm(self, event_id=None, ch=None):
    #     tree = uproot.open("%s:daq" % self.if_path)
    #     cut_str = "event_id == %d" % event_id
    #     adc = tree.arrays(self.ch_names, cut_str)
    #
    #     self.wfm.display(ch)
    #
    # def display_ch_hits(self, event_id=None):
    #     """here or a separate toolbox class??? """
    #     pass

def main(argv):
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='Data Reconstruction Offline Package')
    parser.add_argument('--start_id', type=int, default=0, help='Optional. start process from start_id (default: 0)')
    parser.add_argument('--end_id', type=int, default=MAX_N_EVENT, help='Optional. stop process at end_id (defalt: Arbiarty large)')
    parser.add_argument('--output_dir', type=str, default="", help='Optional. Directory where output file goes. If not specified, same directory as the input file.' )
    required = parser.add_argument_group('Required Arguments')
    required.add_argument('-i', '--if_path', type=str, help='Required. full path to the raw data file', required=True)
    required.add_argument('-c', '--yaml', type=str, help='Required. path to the yaml config file', required=True)
    args = parser.parse_args()

    # RunDROP class is at the top of food-chain
    run = RunDROP(args)

    # RQWriter creates output file, fill, and dump
    writer = RQWriter(args, basket_size=run.batch_size)
    writer.create_output()

    batch_list = uproot.iterate('%s:daq' % args.if_path, step_size=run.batch_size)
    i = 0
    for batch in batch_list:
        run.process_batch(batch, writer)
        i += 1
        # show progress
        pct = float(run.batch_size*i/run.n_event_proc*100)
        print("processed %dth batch, %.1f percent completed" % (i, pct))

    # write run tree once per file
    writer.dump_run_rq({
    'n_boards': [run.n_boards],
    'n_trg_read': [run.n_trg_read],
    'n_event_proc': [run.n_event_proc],
    'leftover_event_id': [run.leftover_event_id],
    'ch_id': [run.ch_id]
    })

    # remeber to close file
    writer.close()

if __name__ == "__main__":
   main(sys.argv[1:])

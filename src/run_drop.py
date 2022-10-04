"""
DROP convert raw waveform to reduced qualities.

Contact:
X. Xiang <xxiang@bnl.gov>
"""
import argparse
import sys
from numpy import array, isscalar, uint16, uint32
import numpy as np
from enum import Enum
import uproot
import pandas as pd
import os
import re
from datetime import datetime

from yaml_reader import YamlReader
from waveform import Waveform
from pulse_finder import PulseFinder
from rq_writer import RQWriter

MAX_N_EVENT = 999999999 # Arbiarty large
YAML_DIR = os.environ['YAML_DIR']


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
        # config
        self.cfg  = YamlReader(args.yaml)

        # variable
        self.batch_id = 0
        self.batch = None
        self.load_run_info()
        self.load_pmt_info()
        self.sanity_check()

    def sanity_check(self):
        '''
        Collection of check before running
        '''
        # check ROI in config
        roi_start = np.array(self.cfg.roi_start_ns)
        roi_end = np.array(self.cfg.roi_end_ns)
        if len(roi_start) != len(roi_end):
            sys.exit('Different list length between roi_start and roi_end.')
        if np.any(roi_end<=roi_start):
            sys.exit('roi_end must be strictly larger than roi_start')
        return None

    def extract_datetime_from_str(self, s):
        """
        Extract datatime from a str. The datetime must follow the fixed format:
        YYmmddTHHMM
        """
        match = re.search(r'\d{6}T\d{4}', s)
        try:
            dt = datetime.strptime(match.group(), '%y%m%dT%H%M')
            return dt
        except ValueError:
            print('Fail finding the datetime string from path: %s' % s)

    def load_run_info(self):
        """
        Load run_info tree, which contains only one entry.

        Notes:
            Not yet possible to save str via uproot. Use numbering convension:
            100*boardId + chID. For example, 211 means board 2, channel 11, or
            `adc_b2_ch11`.
        """
        f = uproot.open(self.if_path)
        dt = self.extract_datetime_from_str(self.if_path)
        self.start_year = uint16(dt.year)
        self.start_month = uint16(dt.month)
        self.start_day= uint16(dt.day)
        self.start_hour= uint16(dt.hour)
        self.start_minute= uint16(dt.minute)
        b_names = ['n_boards', 'n_event_proc', 'n_trg_read', 'leftover_event_id', 'active_ch_id']
        a = f['run_info'].arrays(b_names, library='np')
        self.n_boards = uint16(a['n_boards'][0])
        self.n_trg_read= uint32(a['n_trg_read'][0])
        self.n_event_proc = uint32(a['n_event_proc'][0])
        self.leftover_event_id = uint32(a['leftover_event_id'][0])
        tmp = a['active_ch_id'][0]
        if isscalar(tmp): # if only 1 active channels, tmp is a scalar and sort will fail
            tmp = [tmp]
        self.ch_id = sorted(uint16(tmp))
        self.ch_names = ["adc_b%d_ch%d" % (i // 100, i % 100) for i in self.ch_id]
        self.ch_name_to_id_dict = dict(zip(self.ch_names, self.ch_id))
        return None

    def load_pmt_info(self):
        """
        PMT calibration results are saved in a csv file
        The path to the csv file is specified in yaml config file
        """
        fpath = YAML_DIR + '/' +self.cfg.spe_fit_results_file
        self.spe_mean = {}
        try:
            df = pd.read_csv(fpath)
            df.set_index('ch_name', inplace=True)
            self.spe_fit_results  = df # to be saved in root
            ch_names = df.index
            for ch in ch_names:
                self.spe_mean[ch] = float(df['spe_mean'][ch])
        except:
            for ch in self.ch_names:
                self.spe_mean[ch] = 1.6
            print("WARNING: your spe_fit_results_file cannot be load properly!")
            print('WARNING: Use 1.6 pC as spe_mean for all PMTs')

    def process_batch(self, batch, writer:RQWriter):
        '''
        Process one batch at a time. Batch size is defined in the yaml file.

        Args:
        - batch (high-level awkward array): a collection of raw events
        - writer (RQWriter). If None, nothing to fill & write, but save to memory.
        '''
        # save ref for later ease of access
        self.batch = batch

        # reset writer
        if writer is None:
            self.wfm_list = []
            self.pf_list = []
        else:
            writer.reset()

        # create waveform, PulseFinder,
        wfm = Waveform(self.cfg)
        wfm.ch_names = self.ch_names
        wfm.ch_id = self.ch_id
        wfm.ch_name_to_id_dict=self.ch_name_to_id_dict
        wfm.n_boards = self.n_boards
        wfm.spe_mean = self.spe_mean

        # create PulseFinder
        pf = PulseFinder(self.cfg, wfm)

        # loop over events in this batch
        for i in range(len(batch)):
            event_id = batch[i].event_id
            event_ttt = batch[i].event_ttt
            if event_id<self.start_id or event_id>=self.end_id:
                continue

            # waveform
            wfm.reset()
            wfm.set_raw_data(batch[i])
            wfm.find_saturation()
            wfm.subtract_flat_baseline()
            #wfm.find_ma_baseline()
            wfm.do_spe_normalization()
            wfm.define_trigger_position()
            wfm.correct_daisy_chain_trg_delay()
            wfm.sum_channels()
            wfm.define_time_axis()
            wfm.integrate_waveform()
            wfm.calc_roi_info()
            wfm.calc_aux_ch_info()

            # pulses finding
            pf.reset()
            pf.wfm = wfm
            pf.find_pulses()
            pf.calc_pulse_ch_info()
            pf.calc_pulse_info()
            # fill rq event structure
            if writer is None:
                self.wfm_list.append(wfm)
                self.pf_list.append(pf)
            else:
                writer.fill(wfm, pf)

        if writer is not None:
            writer.dump_event_rq()
        self.batch_id += 1
        return None

    def show_progress(self):
        """
        print progress on screen
        """
        pct = float(self.cfg.batch_size*self.batch_id/self.n_event_proc*100)
        first_ev_id = self.batch[0].event_id
        last_ev_id = self.batch[-1].event_id
        print('processed event_id [%d ... %d]' % (first_ev_id, last_ev_id), end=' ')
        print("%dth batch, %.1f percent completed" % (self.batch_id, pct))
        return None

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
    print("\nSummary of your config file:")
    print(run.cfg.data)
    print("")

    # RQWriter creates output file, fill, and dump
    n_aux_ch = len(run.cfg.non_signal_channels)
    n_ch = len(run.ch_id)-n_aux_ch
    writer = RQWriter(args, n_ch, n_aux_ch, basket_size=run.cfg.batch_size)
    writer.init_basket_cap = int(run.n_event_proc/run.cfg.batch_size)+2
    writer.create_output()

    batch_list = uproot.iterate('%s:daq' % args.if_path, step_size=run.cfg.batch_size)

    for batch in batch_list:
        run.process_batch(batch, writer)
        run.show_progress()

    # write run tree once per file
    # run rq includes from raw root data, and yaml config
    # (uproot cannot save string; so ASCII->int->ASCII for spe_fit_results_file)
    writer.dump_run_rq({
        'start_year': [run.start_year],
        'start_month': [run.start_month],
        'start_day': [run.start_day],
        'start_hour': [run.start_hour],
        'start_minute': [run.start_minute],
        'n_boards': [run.n_boards],
        'n_trg_read': [run.n_trg_read],
        'n_event_proc': [run.n_event_proc],
        'leftover_event_id': [run.leftover_event_id],
        'ch_id': [run.ch_id],
        'cfg_batch_size': [run.cfg.batch_size],
        'cfg_post_trigger': [run.cfg.post_trigger],
        'cfg_dgtz_dynamic_range_mV': [run.cfg.dgtz_dynamic_range_mV],
        'cfg_non_signal_channels': [[run.ch_name_to_id_dict[ch] for ch in run.cfg.non_signal_channels]],
        'cfg_bottom_pmt_channels': [[run.ch_name_to_id_dict[ch] for ch in run.cfg.bottom_pmt_channels]],
        'cfg_side_pmt_channels': [[run.ch_name_to_id_dict[ch] for ch in run.cfg.side_pmt_channels]],
        'cfg_spe_fit_results_file': [[ord(i) for i in run.cfg.spe_fit_results_file]],
        'cfg_daisy_chainr': [run.cfg.daisy_chain],
        'cfg_apply_high_pass_filter': [run.cfg.apply_high_pass_filter],
        'cfg_high_pass_cutoff_Hz': [run.cfg.high_pass_cutoff_Hz],
        'cfg_moving_avg_length': [run.cfg.moving_avg_length],
        'cfg_sigma_above_baseline': [run.cfg.sigma_above_baseline],
        'cfg_pre_pulse': [run.cfg.pre_pulse],
        'cfg_post_pulse': [run.cfg.post_pulse],
        'cfg_roi_start_ns': [run.cfg.roi_start_ns],
        'cfg_roi_end_ns': [run.cfg.roi_end_ns],
        'cfg_pulse_finder_algo': [run.cfg.pulse_finder_algo],
        'cfg_scipy_pf_pars_distance': [run.cfg.scipy_pf_pars.distance],
        'cfg_scipy_pf_pars_threshold': [run.cfg.scipy_pf_pars.threshold],
        'cfg_scipy_pf_pars_height': [run.cfg.scipy_pf_pars.height],
        'cfg_scipy_pf_pars_prominence': [run.cfg.scipy_pf_pars.prominence],
        'cfg_spe_height_threshold': [run.cfg.spe_height_threshold],
    })

    writer.dump_pmt_info(run.spe_fit_results)

    # remeber to close file
    writer.close()

if __name__ == "__main__":
   main(sys.argv[1:])

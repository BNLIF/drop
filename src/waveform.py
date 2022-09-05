'''
One waveform per event.

Outline
- baseline subtraction per channel
- pulse finding
- sum channels
'''
from numpy import zeros, argwhere, trapz, diff, sign, concatenate, quantile, argmax
from numpy import median, cumsum
import numpy as np
import matplotlib.pylab as plt
from matplotlib import cm
from numpy.lib.stride_tricks import sliding_window_view
from utilities import generate_colormap, digitial_butter_highpass_filter
import re
import sys

from yaml_reader import SAMPLE_TO_NS, YamlReader

EPS=1e-6

class Waveform():
    """
    Waveform class. One waveform per event.
    """
    def __init__(self, cfg: YamlReader):
        if cfg is not None:
            self.cfg = cfg
        self.ch_names = None
        self.ch_id = None
        self.ch_name_to_id_dict= None
        self.n_boards = None
        self.spe_mean = None
        self.reset()
        return None

    def reset(self):
        """
        Variables that needs to be reset from event to event
        """
        # from raw data
        self.raw_data = None

        # amplitude is baseline subtracted waveform, in unit of mV or PE
        self.amp_mV ={}
        self.amp_pe={}
        self.amp_pe_int={} # accumulated (integrated) waveform, PE

        # calculated baseline
        self.flat_base_mV = {}
        self.flat_base_std_mV = {}
        self.flat_base_pe = {}
        self.flat_base_std_pe = {}
        self.ma_base_pe = {} # moving average mean
        self.ma_base_std_pe = {} # moving average std

    def set_raw_data(self, val):
        self.raw_data = val
        self.event_id = val.event_id
        self.event_ttt = val.event_ttt
        self.event_sanity=val.event_sanity

    def define_trigger_position(self):
        """
        Time of the first trigger arrived.
        """
        if self.cfg.daisy_chain:
            for ch in self.ch_names:
                if '_b1' in ch:
                    n_samp = len(self.amp_mV[ch])
                    pre_trg_frac = 1.0-self.cfg.post_trigger
                    self.trg_pos = int(n_samp*pre_trg_frac)
                    self.trg_time_ns = self.trg_pos*(SAMPLE_TO_NS)
                    return None
        else:
            print('Sorry pal. Fan-out not yet implemented.')

    def get_flat_baseline(self, val):
        """
        define a flat baseline. Find the median and std.

        Input:
            val: array

        Return:
            float, float
        """
        qx = quantile(val, [0.15865, 0.5, 0.84135]) #med, and central 68%
        return qx[1], abs(qx[2]-qx[0])/2

    def subtract_flat_baseline(self):
        """
        Very basic
        Baseline is avg over all excluding trigger regions
        """
        if self.ch_names is None:
            sys.exit('ERROR: Waveform::ch_names is not specified.')

        adc_to_mV = self.cfg.dgtz_dynamic_range_mV/(2**14-1)
        for ch in self.ch_names:
            val = self.raw_data[ch].to_numpy() # numpy is faster
            med, std = self.get_flat_baseline(val)
            self.flat_base_mV[ch] = med # save a copy
            self.flat_base_std_mV[ch] = std # save a copy
            amp = -(val-med)
            if self.cfg.apply_high_pass_filter:
                cutoff_Hz = self.cfg.high_pass_cutoff_Hz
                amp = digitial_butter_highpass_filter(amp, cutoff_Hz)
            self.amp_mV[ch] = amp*adc_to_mV
        return None

    def do_spe_normalization(self):
        """
        Do SPE normalization for all signal channels
        Muon paddle is considered non-signal channel, and hence not SPE normalized
        """
        if self.spe_mean is None:
            sys.exit('ERROR: spe_mean not specified in Waveform. Unable to normalized.')

        for ch, val in self.amp_mV.items():
            if ch in self.cfg.non_signal_channels:
                continue
            spe_mean = self.spe_mean[ch]
            self.amp_pe[ch] = val/50/spe_mean
            self.flat_base_pe[ch] = self.flat_base_mV[ch]/50/spe_mean
            self.flat_base_std_pe[ch] = self.flat_base_std_mV[ch]/50/spe_mean
        return None

    def correct_daisy_chain_trg_delay(self):
        """
        Shift a channel's waveform based on which board it is
        boardId is baked into ch_name.
        arr: array
        ch_name: str
        """
        dT_ns = 48 # externally calibrated parameter
        dS = dT_ns//int(SAMPLE_TO_NS)
        for ch, a in self.amp_pe.items():
            a_corr = a.copy()
            if "_b1" in ch:
                a_corr=a[dS*2:]
            elif "_b2" in ch:
                a_corr=a[dS:-dS]
            elif "_b3" in ch:
                a_corr=a[0:-dS*2]
            else:
                print("ERROR in correct_trg_delay: invalid boardId")
                return None
            self.amp_pe[ch] = a_corr
        self.trg_pos -= dS*2
        self.trg_time_ns -= dT_ns*2

    def sum_channels(self):
        """
        Sum up channels
        """
        tot_pe = 0
        bt_pe = 0
        side_pe=0
        for ch, val in self.amp_pe.items():
            if 'adc_' in ch:
                tot_pe += val
                if ch in self.cfg.bottom_pmt_channels:
                    bt_pe += val
                if ch in self.cfg.side_pmt_channels:
                    side_pe += val

        self.amp_pe['sum'] = tot_pe
        med, std = self.get_flat_baseline(tot_pe)
        self.flat_base_pe['sum'] = med
        self.flat_base_std_pe['sum'] = std
        self.amp_pe['sum_bot'] = bt_pe
        self.amp_pe['sum_side'] = side_pe
        return None

    def integrate_waveform(self):
        """
        integrated waveform
        """
        for ch, val in self.amp_pe.items():
            self.amp_pe_int[ch] = cumsum(val)*(SAMPLE_TO_NS) # adc*ns

    def find_ma_baseline(self):
        n = self.cfg.moving_avg_length
        win = np.ones(n)
        for ch in self.ch_names:
            a = self.amp_mV
            ma =  np.convolve(a, win/n, mode='valid')
            base = np.concatenate(([val[k] for k in range(n-1)],ma))
            std = np.std(a - base) # std after subtraction
            self.ma_base_pe[ch]=base.copy()
            self.ma_base_std_pe[ch] = std # bs stands for baseline subtracted
        return None

    def find_roi_area(self):
        """
        Calc Integral in the Region of Interest (ROI) whose start_ns and end_ns
        are defined in yaml config file.

        Notes:
            roi_start_ns and roi_end_ns are defined with respect to trigger time
        """
        self.roi_area_pe=[]
        for i in range(len(self.cfg.roi_start_ns)):
            start=self.trg_pos + (self.cfg.roi_start_ns[i]//int(SAMPLE_TO_NS))
            end=self.trg_pos + (self.cfg.roi_end_ns[i]//int(SAMPLE_TO_NS))
            if start<0:
                start=0
            roi_a={}
            for ch, val in self.amp_pe_int.items():
                if end>=len(val):
                    end = len(val)-1
                roi_a[ch] = val[end]-val[start]
            self.roi_area_pe.append(roi_a)
        return None

    def find_roi_height(self):
        """
        calc the height within the Region of Interest (ROI) whose start_ns and
        end_ns are defined in yaml config file

        Notes:
            roi_start_ns and roi_end_ns are defined with respect to trigger time
        """
        self.roi_height_pe=[]
        for i in range(len(self.cfg.roi_start_ns)):
            start= self.trg_pos + (self.cfg.roi_start_ns[i]//int(SAMPLE_TO_NS))
            end= self.trg_pos + (self.cfg.roi_end_ns[i]//int(SAMPLE_TO_NS))

            if start<0:
                start=0
            height={}
            for ch, val in self.amp_pe.items():
                if end>=len(val):
                    end = len(val)-1
                height[ch] = np.max(val[start:end])
            self.roi_height_pe.append(height)
        return None

    def calc_aux_ch_info(self):
        """
        Reconstruct simple variables for non-signal channels (auxiliary channel)
        For example, the paddles are non-signal channels that provides auxiliary info
        """
        self.aux_ch_area_mV={}
        for ch in self.cfg.non_signal_channels:
            a=self.amp_mV[ch]
            pp = argmax(a) # peak position
            start=np.max([pp-50, 0])
            end = np.min([pp+50, len(a)-1])
            area = np.sum(a[start:end])*SAMPLE_TO_NS
            self.aux_ch_area_mV[ch] = area

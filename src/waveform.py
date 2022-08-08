'''
One waveform per event.

Outline
- baseline subtraction per channel
- pulse finding
- sum channels
'''
from numpy import zeros, argwhere, trapz, diff, sign, concatenate, quantile
from numpy import median, cumsum
import numpy as np
import matplotlib.pylab as plt
from matplotlib import cm
from numpy.lib.stride_tricks import sliding_window_view
from utilities import generate_colormap, digitial_butter_highpass_filter
import re
import sys

from yaml_reader import ADC_RATE_HZ

EPS=1e-6

class Waveform():
    """
    Waveform class. One waveform per event.
    """
    def __init__(self, config: dict):
        if config is not None:
            self.apply_high_pass_filter = bool(config['apply_high_pass_filter'])
            self.high_pass_cutoff_Hz = float(config['high_pass_cutoff_Hz'])
            #self.bs_algo = int(config['baseline_subtraction_algorithim'])
            self.ma_len = int(config['moving_avg_length'])
            self.sigma_thr = float(config['sigma_above_baseline'])
            self.daq_len = int(config['daq_length'])
            self.post_tri = float(config['post_trigger'])
            self.roi_start = config['roi_start']
            self.roi_end = config['roi_end']
            self.pre_roi_length = config['pre_roi_length']
            self.find_trigger_position() # art of finding trigger position
        self.ch_names = None
        self.ch_id = None
        self.n_boards = None
        self.reset()
        return None

    def reset(self):
        """
        Variables that needs to be reset from event to event
        """
        # from raw data
        self.raw_data = None
        # calculated stuff
        self.ma_base = {} # baseline mean
        self.ma_bs_std = {} # baseline std
        self.amplitude={} # amplitude is baseline subtracted trace
        self.amplitude_int={} # integrated amplitude

    def set_n_boards(self, val):
        self.n_boards = val
    def set_ch_names(self, val):
        self.ch_names = val
    def set_ch_id(self, val):
        self.ch_id = val
    def set_raw_data(self, val):
        self.raw_data = val
        self.event_id = val.event_id
        self.event_ttt = val.event_ttt

    def find_trigger_position(self):
        """
        finding trigger position (t0)
        """
        tmp = int(self.daq_len*(1.0-self.post_tri)) # trigger position
        self.tri_pos  = tmp - 20 # Daisy chain trigger delay
        return None

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
            sys.exit('ERROR: Waveform::ch_names is not specified. Use Waveform::set_ch_names()')
        for ch in self.ch_names:
            val = self.raw_data[ch].to_numpy() # numpy is faster
            med, std = self.get_flat_baseline(val)
            amp = -(val-med)
            if self.apply_high_pass_filter:
                cutoff_Hz = self.high_pass_cutoff_Hz
                amp = digitial_butter_highpass_filter(amp, cutoff_Hz)
            self.amplitude[ch] = amp
        return None

    def sum_channels(self):
        """
        Sum all channels
        """
        tot = 0
        for ch, val in self.amplitude.items():
            tot += val
        self.amplitude['sum'] = tot

        # def baseline for sum channel
        mean, std = self.get_flat_baseline(tot)
        self.base_mean['sum'], self.base_std['sum'] = mean, std
        return None

    def integrate_waveform(self):
        """
        integrated waveform
        """
        for ch, val in self.amplitude.items():
            self.amplitude_int[ch] = cumsum(val)*(1e9/ADC_RATE_HZ) # adc*ns

    def find_ma_baseline(self):
        n = self.ma_len
        win = np.ones(n)
        for ch in self.ch_names:
            a = self.amplitude # after subtract flat base, and reverse polarity
            ma =  np.convolve(a, win/n, mode='valid')
            base = np.concatenate(([val[k] for k in range(n-1)],ma))
            std = np.std(a - base) # std after subtraction
            self.ma_base[ch]=base.copy()
            self.ma_bs_std[ch] = std # bs stands for baseline subtracted

    def find_roi_area(self):
        self.roi_area_adc=[]
        for i in range(len(self.roi_start)):
            start=self.roi_start[i]
            end=self.roi_end[i]
            # pre_roi = start-self.pre_roi_length
            roi_a={}
            for ch, val in self.amplitude_int.items():
                roi_a[ch] = val[end]-val[start]
            self.roi_area_adc.append(roi_a)
        return None

    def find_roi_height(self):
        # do baseline subtraction if haven't done so
        if bool(self.amplitude)==False:
            self.do_baseline_subtraction()
            self.sum_channels()

        self.roi_height_adc=[]
        for i in range(len(self.roi_start)):
            start=self.roi_start[i]
            end=self.roi_end[i]
            height={}
            for ch, val in self.amplitude.items():
                height[ch] = np.max(val[start:end])
            self.roi_height_adc.append(height)
        return None

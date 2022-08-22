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

from yaml_reader import ADC_RATE_HZ, YamlReader

EPS=1e-6

class Waveform():
    """
    Waveform class. One waveform per event.
    """
    def __init__(self, cfg: YamlReader):
        if cfg is not None:
            self.cfg = cfg
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
        # calculated baseline
        self.ma_base = {} # moving average mean
        self.ma_base_std = {} # moving average std
        self.flat_base = {} # flat baseline mean
        self.flat_base_std = {} #flat baseline std

        # amplitude is baseline subtracted waveform
        self.amp_mV={} #  in mV
        self.amp_mV_int={} # accumulated (integrated) waveform), mV*ns
        self.amp_pe={} # pe/ns
        self.amp_pe_int={} # accumulated (integrated) waveform, PE

    def set_raw_data(self, val):
        self.raw_data = val
        self.event_id = val.event_id
        self.event_ttt = val.event_ttt

    def find_trigger_position(self):
        """
        Trigger position
        """
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
            self.flat_base[ch] = med # save a copy
            self.flat_base_std[ch] = std # save a copy
            amp = -(val-med)
            if self.cfg.apply_high_pass_filter:
                cutoff_Hz = self.cfg.high_pass_cutoff_Hz
                amp = digitial_butter_highpass_filter(amp, cutoff_Hz)
            self.amp_mV[ch] = self.correct_trg_delay(amp, ch)
        return None

    def calc_amp_pe(self):
        pass

    def sum_channels(self):
        """
        Sum all channels
        """
        tot = 0
        for ch, val in self.amp_mV.items():
            tot += val
        self.amp_mV['sum'] = tot

        # def baseline for sum channel
        med, std = self.get_flat_baseline(tot)
        self.flat_base['sum'] = med
        self.flat_base_std['sum'] = std
        return None

    def correct_trg_delay(self, arr, ch_name):
        """
        Shift a channel's waveform based on which board it is
        boardId is baked into ch_name.
        arr: array
        ch_name: str
        """
        arr_corr = arr.copy()
        dT_ns = 48 # externally calibrated
        dS = dT_ns//2
        if "_b1" in ch_name:
            arr_corr=arr[dS*2:]
        elif "_b2" in ch_name:
            arr_corr=arr[dS:-dS]
        elif "_b3" in ch_name:
            arr_corr=arr[0:-dS*2]
        else:
            print("ERROR")
            return None
        return arr_corr

    def integrate_waveform(self):
        """
        integrated waveform
        """
        for ch, val in self.amp_mV.items():
            self.amp_mV_int[ch] = cumsum(val)*(1e9/ADC_RATE_HZ) # adc*ns

    def find_ma_baseline(self):
        n = self.cfg.moving_avg_length
        win = np.ones(n)
        for ch in self.ch_names:
            a = self.amp_mV # after subtract flat base, and reverse polarity
            ma =  np.convolve(a, win/n, mode='valid')
            base = np.concatenate(([val[k] for k in range(n-1)],ma))
            std = np.std(a - base) # std after subtraction
            self.ma_base[ch]=base.copy()
            self.ma_base_std[ch] = std # bs stands for baseline subtracted
        return None

    def find_roi_area(self):
        self.roi_area_adc=[]
        for i in range(len(self.cfg.roi_start)):
            start=self.cfg.roi_start[i]
            end=self.cfg.roi_end[i]

            # pre_roi = start-self.cfg.pre_roi_length
            roi_a={}
            for ch, val in self.amp_mV_int.items():
                roi_a[ch] = val[end]-val[start]
            self.roi_area_adc.append(roi_a)
        return None

    def find_roi_height(self):
        # do baseline subtraction if haven't done so
        if bool(self.amp_mV)==False:
            self.do_baseline_subtraction()
            self.sum_channels()

        self.roi_height_adc=[]
        for i in range(len(self.cfg.roi_start)):
            start=self.cfg.roi_start[i]
            end=self.cfg.roi_end[i]
            height={}
            for ch, val in self.amp_mV.items():
                height[ch] = np.max(val[start:end])
            self.roi_height_adc.append(height)
        return None

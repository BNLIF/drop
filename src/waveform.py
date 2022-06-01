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
            self.roll_len = int(config['rolling_length'])
            self.sigma_thr = float(config['sigma_above_baseline'])
            self.daq_len = int(config['daq_length'])
            self.post_tri = float(config['post_trigger'])
            self.roi_start = config['roi_start']
            self.roi_end = config['roi_end']
            self.pre_roi_length = config['pre_roi_length']
            self.trigger_position() # art of finding trigger position
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
        self.base_mean = {} # baseline mean
        self.base_std = {} # baseline std
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

    def trigger_position(self):
        """
        finding trigger position (t0)
        """
        tmp = int(self.daq_len*(1.0-self.post_tri)) # trigger position
        self.tri_pos  = tmp - 20 # Daisy chain trigger delay
        return None

    def get_flat_baseline(self, val):
        """
        define a flat baseline away from trigger
        Input:
            - val: array
        """
        t0=self.tri_pos
        pre = val[:t0-20]
        post = val[t0+50:]
        base = concatenate([pre, post])
        qx = quantile(base, [0.15865, 0.5, 0.84135]) #central 68%
        return qx[1], abs(qx[2]-qx[0])

    def do_baseline_subtraction(self):
        """
        Very basic
        Baseline is avg over all excluding trigger regions
        """
        if self.ch_names is None:
            sys.exit('ERROR: Waveform::ch_names is not specified. Use Waveform::set_ch_names()')

        for ch in self.ch_names:
            val = self.raw_data[ch].to_numpy() # numpy is faster
            mean, std = self.get_flat_baseline(val)
            self.base_mean[ch], self.base_std[ch] = mean, std
            amp = -(val-self.base_mean[ch])
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

    def rolling_baseline(self):
        """work in progress"""
        med = zeros(self.daq_len-10)
        std =zeros(self.daq_len)
        for ch in self.ch_names:
            val = self.raw_data[ch]
            v = sliding_window_view(val, self.roll_len)
            roll_start = self.roll_len-1
            med[roll_start:] = v.median(axis=-1)
            qx = quantile(v, [0.15865, 0.84135], axis=-1)
            std[roll_start:] = abs(qx[1]-qx[0])
            self.roll_base_med[ch]=med.copy()
            self.roll_base_std[ch]=std.copy()

    def do_rolling_baseline_subtraction(self):
        """work in progress"""
        pass

    def find_roi_area(self):
        # do baseline subtraction if haven't done so
        if bool(self.amplitude)==False:
            self.do_baseline_subtraction()
            self.sum_channels()

        self.roi_area_adc=[]
        for i in range(len(self.roi_start)):
            start=self.roi_start[i]
            end=self.roi_end[i]
            # pre_roi = start-self.pre_roi_length
            roi_a={}
            for ch, val in self.amplitude.items():
                roi_a[ch]=np.sum(val[start:end])
            self.roi_area_adc.append(roi)
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

    # def display(self, ch=None):
    #     '''
    #     ch: string, ex. b1_ch0, sum. Default: None (all)
    #     '''
    #     # plotting style
    #     plt.rcParams['axes.grid'] = True
    #
    #     if ch is None or ch=='all':
    #         fig = plt.figure(figsize=[9,3*self.n_boards])
    #         cmap = generate_colormap(16)
    #
    #
    #         for k in range(self.n_boards):
    #             ax1 = plt.subplot(self.n_boards,1,1)
    #         ax2 = plt.subplot(self.n_boards,1,2)
    #         for ch in sorted(self.ch_names):
    #             val = self.raw_data[ch]
    #             # get end digits, which is ch number on a board
    #             ch_id = int(re.match('.*?([0-9]+)$', key).group(1))
    #             if 'b1_' in ch:
    #                 label='ch%d' % ch_id
    #                 ax1.plot(val, label=label, color=cmap.colors[ch_id])
    #                 ax1.set_title('event_id=%d, Board 1' % self.event_id)
    #             if 'b2_' in ch:
    #                 label='ch%d' % ch_id
    #                 ax2.plot(val, label=label, color=cmap.colors[ch_id])
    #                 ax2.set_title('event_id=%d, Board 2' % self.event_id)
    #             if 'b3_' in ch:
    #                 label='ch%d' % ch_id
    #                 ax3.plot(val, label=label, color=cmap.colors[ch_id])
    #                 ax3.set_title('event_id=%d, Board 3' % self.event_id)
    #         ax1.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    #     else:
    #         fig = plt.figure(figsize=[8,4])
    #         plt.subplot(111)
    #         if isinstance(ch, str):
    #             a = self.amplitude[ch]
    #             plt.plot(a, label=ch)
    #             plt.plot()
    #             plt.plot(zeros(a), '--', color='gray', label='flat baseline')
    #         elif isinstance(ch, list):
    #             for t in ch:
    #                 plt.plot(self.traces[t], label=t)
    #         plt.legend(loc=0)
    #
    #     ymin, ymax = plt.ylim()
    #     plt.ylim(ymax=ymax + (ymax-ymin)*.15)
    #     plt.xlabel('Samples')
    #     plt.ylabel('ADC')
    #     plt.grid()
    #     #plt.show()

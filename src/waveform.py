'''
Outline
- baseline subtraction per channel
- pulse finding
- sum channels
'''
from numpy import zeros, argwhere, trapz, diff, sign, concatenate, quantile
import numpy as np
import matplotlib.pylab as plt
from matplotlib import cm
from scipy.signal import find_peaks

from caen_reader import RawDataFile
from caen_reader import RawTrigger
from numpy.lib.stride_tricks import sliding_window_view

from utilities import *
import re

EPS=1e-6


class Waveform(RawTrigger):
    """
    Waveform class is derived from RawTrigger class
    """
    def __init__(self, config):
        super(RawTrigger, self).__init__()
        self.roll_len = int(config['rolling_length'])
        self.sigma_thr = float(config['sigma_above_baseline'])
        self.daq_len = int(config['daq_length'])
        self.post_tri = float(config['post_trigger'])
        self.pre_pulse = int(config['pre_pulse'])
        self.post_pulse = int(config['post_pulse'])
        self.sfp_dist = int(config['scipy_find_peaks']['distance'])
        self.sfp_thre = config['scipy_find_peaks']['threshold']
        self.sfp_heig = config['scipy_find_peaks']['height']
        self.roi_start = config['roi_start']
        self.roi_end = config['roi_end']
        self.pre_roi_length = config['pre_roi_length']
        self.trigger_position() # art of finding trigger position

        self.event_id=-1

        # calc in do_baseline_subtraction
        self.base_mean = {} # baseline mean
        self.base_std = {} # baseline std
        self.amplitude={} # amplitude is baseline subtracted trace
        return None

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
        post= val[t0+50:]
        base = concatenate([pre, post])
        qx = quantile(base, [0.15865, 0.84135]) #central 68%
        return np.median(base), abs(qx[1]-qx[0])

    def do_baseline_subtraction(self):
        """
        Very basic
        Baseline is avg over all excluding trigger regions
        """
        for ch, val in self.traces.items():
            mean, std = self.get_flat_baseline(val)
            self.base_mean[ch], self.base_std[ch] = mean, std
            self.amplitude[ch] = -(val-self.base_mean[ch])
            # todo: convert ADC to to mV/ns
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

    def scipy_find_peaks(self):
        """
        Scipy find_peaks functions
        """
        self.do_baseline_subtraction()
        self.sum_channels()
        self.peaks={}
        for ch, val in self.amplitude.items():
            a = self.amplitude[ch]
            std = self.base_std[ch]
            peaks, _ = find_peaks(
            a,
            distance=self.sfp_dist,
            threshold=self.sfp_thre*std,
            height=self.sfp_heig*std
            )
            self.peaks[ch] = peaks #peak position
        return None

    def get_spe(self, ch='sum'):
        """ Work in Progress """
        if self.peaks[ch].size == 0:
            return []

        pls=Pulses()
        pls.start = self.peaks[ch]-4
        pls.end = pls.start+4
        for i in range(len(self.peaks[ch])):
            pls.height.append( np.max(self.amplitude[ch][start:end]) )
            pls.area.append( np.sum(self.amplitude[ch][start:end]) )
            pulses.append(pls)
        return pulses

    def rolling_baseline(self):
        """work in progress"""
        med = zeros(self.daq_len-10)
        std =zeros(self.daq_len)
        for ch, val in self.traces.items():
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

    def integrate_roi(self):
        # do baseline subtraction if haven't done so
        if bool(self.amplitude)==False:
            self.do_baseline_subtraction()
            self.sum_channels()

        self.roi_list=[]
        for i in range(len(self.roi_start)):
            start=self.roi_start[i]
            end=self.roi_end[i]
            pre_roi = start-self.pre_roi_length
            roi={}
            roi_sum = 0.
            for ch, val in self.amplitude.items():
                base = np.median(val[pre_roi:start]) # not to confused with built-in mean()
                roi[ch]=np.sum(-(val[start:end]-base))*(end-start)
                roi_sum += roi[ch]
            roi['sum']=roi_sum
            self.roi_list.append(roi)
        return None

    def roi_max_height(self):
        """Work in Progress"""
        # do baseline subtraction if haven't done so
        if bool(self.amplitude)==False:
            self.do_baseline_subtraction()
            self.sum_channels()

        self.roi_height=[]
        for i in range(len(self.roi_start)):
            start=self.roi_start[i]
            end=self.roi_end[i]
            height={}
            for ch, val in self.amplitude.items():
                height[ch] = np.max(val[start:end])
            self.roi_height.append(height)
        return None

    def display(self, ch=None):
        '''
        ch: string, ex. b1_ch0, sum. Default: None (all)
        '''
        # plotting style
        plt.rcParams['axes.grid'] = True

        if ch is None or ch=='all':
            fig = plt.figure(figsize=[9,8])
            cmap = generate_colormap(16)
            ax1 = plt.subplot(211)
            ax2 = plt.subplot(212)
            for trace in sorted(self.traces.items()):
                key=trace[0] # key ex: b1_ch0
                # get end digits, which is ch number on a board
                ch_id = int(re.match('.*?([0-9]+)$', key).group(1))
                if 'b1_' in trace[0]:
                    label='ch%d' % ch_id
                    ax1.plot(trace[1], label=label, color=cmap.colors[ch_id])
                    ax1.set_title('event_id=%d, Board 1' % self.event_id)
                if 'b2_' in trace[0]:
                    label='ch%d' % ch_id
                    ax2.plot(trace[1], label=label, color=cmap.colors[ch_id])
                    ax2.set_title('event_id=%d, Board 2' % self.event_id)
            ax1.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        else:
            fig = plt.figure(figsize=[9,4])
            plt.subplot(111)
            if isinstance(ch, str):
                a = self.amplitude[ch]
                p = self.peaks[ch]
                plt.plot(a, label=ch)
                plt.plot()
                plt.plot(np.zeros_like(a), '--', color='gray', label='flat baseline')
                plt.plot(p, a[p], "x")
            elif isinstance(ch, list):
                for t in ch:
                    plt.plot(self.traces[t], label=t)
            plt.legend(loc=0)

        ymin, ymax = plt.ylim()
        plt.ylim(ymax=ymax + (ymax-ymin)*.15)
        plt.xlabel('Samples')
        plt.ylabel('ADC')
        plt.grid()
        #plt.show()
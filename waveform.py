'''
Outline
- baseline subtraction per channel
- pulse finding
- sum channels
'''
from numpy import zeros, argwhere, trapz, diff, sign, concatenate
import numpy as np
import matplotlib.pylab as plt
from scipy.signal import find_peaks

from caen_reader import RawDataFile
from caen_reader import RawTrigger
from numpy.lib.stride_tricks import sliding_window_view

EPS=1e-6

class Pulses:
    pulses_start = []
    pulses_end = []
    area = []

class Waveform(RawTrigger):

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

    def def_flat_baseline(self, val):
        """
        define a flat baseline away from trigger
        """
        t0 = int(self.daq_len*(1.0-self.post_tri)) # trigger position
        pre = val[:t0-50]
        post= val[t0+50:]
        base = concatenate([pre, post])
        return np.mean(base), np.std(base)

    def do_baseline_subtraction(self):
        """
        Very basic
        Baseline is avg over all excluding trigger regions
        """
        self.base_mean = {} # baseline mean
        self.base_std = {} # baseline std
        self.amplitude={} # amplitude is baseline subtracted trace
        for ch, val in self.traces.items():
            mean, std = self.def_flat_baseline(val)
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
        mean, std = self.def_flat_baseline(tot)
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



    # def do_rolling_baseline_subtraction(self):
    #     self.find_baseline()
    #
    #     self.pulse_start={}
    #     self.thre={}
    #     avg=zeros(self.daq_len)
    #     std =zeros(self.daq_len)
    #     for ch, val in self.traces.items():
    #         v = sliding_window_view(val, self.roll_len)
    #         roll_start = self.roll_len-1
    #         avg[roll_start:] = v.mean(axis=-1)
    #         std[roll_start:] = v.std(axis=-1)
    #         in_mask = val<=avg-std*self.sigma_thr
    #         idx = argwhere(diff(sign(val - std*self.sigma_thr))).flatten()
    #         self.baseline[ch]=avg.copy()
    #         self.pulse_start[ch]=idx.copy()
    #         self.thre[ch]=avg-std*self.sigma_thr
    #     return None



    def integrate_roi(self):
        self.roi_list=[]
        for i in range(len(self.roi_start)):
            start=self.roi_start[i]
            end=self.roi_end[i]
            pre_roi = start-self.pre_roi_length
            roi={}
            roi_sum = 0.
            for ch, val in self.traces.items():
                base = np.mean(val[pre_roi:start]) # not to confused with built-in mean()
                roi[ch]=np.sum(-(val[start:end]-base))*(end-start)
                roi_sum += roi[ch]
            roi['sum']=roi_sum
            self.roi_list.append(roi)
        return None

    def display(self, ch=None):
        '''
        ch: string, ex. b1_ch0, sum. Default: None
        '''
        fig = plt.figure(figsize=[11,5])
        ax = fig.add_subplot(111)
        if ch is None or ch=='all':
            for trace in sorted(self.traces.items()):
                plt.plot(trace[1], label=trace[0])
        else:
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
        ax.legend(loc=0)

        # place a text box in upper left in axes coords with details of event
        textstr = 'File Position: {}\nTrigger Time (us): {}\nEvent Counter: {}'\
            .format(self.filePos, self.triggerTime, self.eventCounter)

        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7))

        ymin, ymax = plt.ylim()
        plt.ylim(ymax=ymax + (ymax-ymin)*.15)
        plt.xlabel('Samples')
        plt.ylabel('Channel')
        plt.grid()
        plt.show()

from numpy import zeros, sort, arange, ndarray, uint32
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from waveform import Waveform

class PulseFinder():
    """
    Finding pulses
    """
    def __init__(self, config: dict, wfm: Waveform):

        # initialize variables
        self.peaks={}
        self.n_pulses = 0
        self.id = []
        self.start = []
        self.end = []
        self.height_adc = []
        self.area_adc = []
        self.coincidence =  []
        # save config param for latter access
        self.pre_pulse = int(config['pre_pulse'])
        self.post_pulse = int(config['post_pulse'])
        self.scipy_param = {
            'distance': int(config['scipy_find_peaks']['distance']),
            'threshold': float(config['scipy_find_peaks']['threshold']),
            'height': float(config['scipy_find_peaks']['height'])
        }
        # waveform
        self.wfm = wfm

    def scipy_find_peaks(self):
        """
        Scipy find_peaks functions
        """
        par = self.scipy_param
        for ch, val in self.wfm.amplitude.items():
            a = self.wfm.amplitude[ch]
            std = self.wfm.base_std[ch]
            peaks, _ = find_peaks(a,
                distance=par['distance'],
                threshold=par['threshold']*std,
                height=par['height']*std
            )
            self.peaks[ch] = peaks #peak position
        return None

    def find_pulses(self):
        if not bool(self.peaks):
            self.scipy_find_peaks()
        # peaks found at sum channel are used to define pulses
        peaks = sort(self.peaks['sum'])

        self.n_pulses = len(peaks)
        amp = self.wfm.amplitude['sum'] # amplitude in adc
        amp_int = self.wfm.amplitude_int['sum'] # integrated amplitude in adc*ns
        if self.n_pulses>0:
            self.id = arange(self.n_pulses, dtype=uint32)
            self.start =peaks-self.pre_pulse
            self.end = peaks+self.post_pulse
            np.place(self.start, self.start<0, 0)
            np.place(self.end, self.end>=len(amp), len(amp)-1)
            self.area_adc = amp_int[self.end]-amp_int[self.start]
            # todo: vectorize pulse height calc
            tmp = []
            for i in self.id:
                # if len(amp[self.start[i]:self.end[i]])==0:
                #     print(i, self.start[i], self.end[i])
                pmax= np.max(amp[self.start[i]:self.end[i]])
                tmp.append( pmax )
            self.height_adc = tmp
        # todo: adjust credential if it's a spe


    def is_spe(self, ch='sum') -> bool:
        """ Work in Progress """
        pass

    def display(self, ch='sum'):
        '''
        A plotting function showcase pulse finder
        ch: string, ex. b1_ch0. Default: sum
        '''
        if isinstance(ch, list):
            print("ERROR: ch is a string, not a list. Use Waveform::display \
            to show multiple channels.")
            return None
        elif isinstance(ch, str):
            plt.rcParams['axes.grid'] = True
            fig = plt.figure(figsize=[8,4])
            a = self.wfm.amplitude[ch]
            plt.plot(a, label=ch)
            p = self.peaks[ch]
            plt.plot(p, a[p], 'x')
            plt.plot(zeros_like(a), '--', color='gray', label='flat baseline')
            plt.legend(loc=0)
            ymin, ymax = plt.ylim()
            plt.ylim(ymax=ymax + (ymax-ymin)*.15)
            plt.xlabel('Samples')
            plt.ylabel('ADC')
        else:
            print("ERROR: ch type is wrong")
            return None

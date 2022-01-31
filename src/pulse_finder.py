import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from waveform import Waveform

MAX_N_PULSES = 100

class PulseFinder():
    """
    Finding pulses
    """
    def __init__(self, config: dict, wfm: Waveform):

        # define pulse variables to be calculate
        self.n_pulses = 0
        self.start = np.zeros(MAX_N_PULSES, dtype=int)
        self.height_adc = np.zeros(MAX_N_PULSES, dtype=int)
        self.area_adc = np.zeros(MAX_N_PULSES, dtype=int)
        self.coincidence =  np.zeros(MAX_N_PULSES, dtype=int)
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
        self.peaks={}
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

    def display(self, ch='sum'):
        '''
        ch: string, ex. b1_ch0. Default: sum
        '''
        if isinstance(ch, list):
            print("ERROR: ch is a string, not a list. Use Waveform::display \
            to show multiple channels.")
            return None
        elif isinstance(ch, str):
            fig = plt.figure(figsize=[8,4])
            a = self.wfm.amplitude[ch]
            plt.plot(a, label=ch)
            p = self.peaks[ch]
            plt.plot(p, a[p], 'x')
            plt.plot(np.zeros_like(a), '--', color='gray', label='flat baseline')
            plt.legend(loc=0)
            ymin, ymax = plt.ylim()
            plt.ylim(ymax=ymax + (ymax-ymin)*.15)
            plt.xlabel('Samples')
            plt.ylabel('ADC')
            plt.grid()
        else:
            print("ERROR: ch type is wrong")
            return None

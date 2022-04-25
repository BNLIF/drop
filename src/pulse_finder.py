from numpy import array, zeros, sort, arange, ndarray, uint32, place, logical_and
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from waveform import Waveform

class PulseFinder():
    """
    Finding pulses.
    """
    def __init__(self, config: dict, wfm: Waveform):
        """Constructor

        Args:
            config (dict): yaml file config in dictionary
            wfm (Waveform): waveform by Waveform class

        Notes:
            Initializes variables. When no pulse found, initial value are used. So
            better to have consistent initial type.
        """
        # save config param for latter access
        self.pre_pulse = int(config['pre_pulse'])
        self.post_pulse = int(config['post_pulse'])
        self.scipy_param = {
            'distance': int(config['scipy_find_peaks']['distance']),
            'threshold': float(config['scipy_find_peaks']['threshold']),
            'height': float(config['scipy_find_peaks']['height'])
        }

        self.reset()

    def reset(self):
        """
        Variables that needs to be reset per event
        """
        self.peaks={} # dict
        self.n_pulses = 0 # int
        self.id = array([]) # type: ndarray
        self.start = array([]) # type: ndarray
        self.end = array([]) # type: ndarray
        self.area_adc = array([]) # type: ndarray
        self.height_adc = [] #type: list
        self.coincidence =  [] #type: list
        self.wfm = None

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
        """Main function of PulseFinder. As the name suggests, find pulses. Only
        run this after baseline subtraction.
        """
        if not bool(self.peaks):
            self.scipy_find_peaks()
        # peaks found at sum channel are used to define pulses
        peaks_sum = sort(self.peaks['sum'])

        self.n_pulses = len(peaks_sum)
        amp = self.wfm.amplitude['sum'] # amplitude in adc
        amp_int = self.wfm.amplitude_int['sum'] # integrated amplitude in adc*ns
        if self.n_pulses>0:
            self.id = arange(self.n_pulses, dtype=uint32)
            self.start =peaks_sum-self.pre_pulse
            self.end = peaks_sum+self.post_pulse
            place(self.start, self.start<0, 0)
            place(self.end, self.end>=len(amp), len(amp)-1)
            self.area_adc = amp_int[self.end]-amp_int[self.start]

            # todo: vectorize the loop
            for i in self.id:
                start = self.start[i]
                end = self.end[i]
                pmax = np.max(amp[start:end])
                self.height_adc.append(pmax)
                coin = 0
                for ch, val in self.peaks.items():
                    if ch=='sum':
                        continue
                    mask = logical_and(val>=start, val<end)
                    if len(val[mask])>0:
                        coin +=1
                self.coincidence.append(coin)
        # todo: adjust credential if it's a spe


    def is_spe(self, ch='sum') -> bool:
        """ Work in Progress """
        pass

    def display(self, ch='sum'):
        '''
        A plotting function showcase pulse finder

        Args:
            ch (str, list):  specified a channel to dispaly.
                ex. b1_ch0, ['b1_ch0', 'b1_ch1']. Default: sum
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

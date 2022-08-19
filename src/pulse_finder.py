from numpy import array, zeros, sort, arange, ndarray, uint32, place, logical_and
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from waveform import Waveform
from yaml_reader import YamlReader

class PulseFinder():
    """
    Finding pulses.
    """
    def __init__(self, cfg: YamlReader, wfm: Waveform):
        """Constructor

        Args:
            cfg (YamlReader): configurations passed in by yaml file
            wfm (Waveform): waveform by Waveform class

        Notes:
            Initializes variables. When no pulse found, initial value are used. So
            better to have consistent initial type.
        """
        self.cfg = cfg
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
        pars = self.cfg.scipy_pf_pars
        for ch, val in self.wfm.amp_mV.items():
            a = self.wfm.amp_mV[ch]
            std = self.wfm.flat_base_std[ch]
            peaks, _ = find_peaks(a,
                distance=pars.distance,
                threshold=pars.threshold*std,
                height=pars.height*std
            )
            self.peaks[ch] = peaks #peak position
        return None

    def find_pulses(self):
        """
        As the name suggests, find pulses. A pulse is defined from a start sample
        to an end sample. Assign unique pulse id starting from 0.

        This function assume pulse is postively polarized, only run this after
        baseline subtraction, and flip polarity. See Waveform::subtract_flat_baseline.
        """
        if not bool(self.peaks):
            self.scipy_find_peaks()
        # peaks found at sum channel are used to define pulses
        peaks_sum = sort(self.peaks['sum'])

        self.n_pulses = len(peaks_sum)
        amp = self.wfm.amp_mV['sum'] # amp_mV in adc
        if self.n_pulses>0:
            self.id = arange(self.n_pulses, dtype=uint32)
            self.start =peaks_sum-self.cfg.pre_pulse
            self.end = peaks_sum+self.cfg.post_pulse
            place(self.start, self.start<0, 0)
            place(self.end, self.end>=len(amp), len(amp)-1)

    def calc_pulse_info(self):
        """
        Calculate pulse info, such as ex area, peak height, coincidence, etc.
        """

        if self.n_pulses<=0:
            return None

        amp_int = self.wfm.amp_mV_int['sum'] # integrated amplitude in adc*ns
        self.area_adc = amp_int[self.end]-amp_int[self.start]
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
        return None


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

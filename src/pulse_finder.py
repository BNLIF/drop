from numpy import array, zeros, sort, arange, ndarray, uint32, uint16, place, logical_and, argsort
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
        self.peak_properties={}
        self.n_pulses = 0 # int
        self.id = None # type: ndarray
        self.start = None
        self.end = None
        self.area_pe = {}
        self.height_pe = {}
        self.coincidence = []
        self.sba = [] # side-bottom-asymmetry
        self.wfm = None

    def scipy_find_peaks(self):
        """
        Scipy find_peaks functions
        """
        pars = self.cfg.scipy_pf_pars
        self.base_std_pe = {}
        self.base_med_pe = {}
        for ch, val in self.wfm.amp_pe.items():
            a = self.wfm.amp_pe[ch]
            qx = np.quantile(a[0:100], q=[0.16, 0.5, 0.84])
            std = abs(qx[2]-qx[0])
            med = qx[1]
            self.base_med_pe[ch] = med
            self.base_std_pe[ch] = std # save a copy
            # std = self.wfm.flat_base_std_pe[ch]
            peaks, prop = find_peaks(a,
                distance=pars.distance,
                threshold=pars.threshold*std,
                height=pars.height*std,
                prominence=pars.prominence
            )
            self.peaks[ch] = peaks #peak position
            self.peak_properties[ch] = prop
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

        # peaks found at sum channel, sorted by prominence
        idx = argsort(self.peak_properties['sum']['prominences'])
        peaks = self.peaks['sum'][idx]
        pprop = {}
        for k, val in self.peak_properties['sum'].items():
            pprop[k] = val[idx]
        self.n_pulses = len(peaks)
        self.id = zeros(self.n_pulses, dtype=uint32)
        self.start = zeros(self.n_pulses, dtype=uint32)
        self.end = zeros(self.n_pulses, dtype=uint32)
        a = self.wfm.amp_pe['sum']
        for i in range(self.n_pulses):
            self.id[i] = i
            pk = peaks[i]
            pk_l = pk
            pk_r = pk
            for j in range(8):
                pk_l -= 1
                left_thresh = self.base_med_pe['sum']
                if a[pk_l]<=left_thresh or pk_l<=0:
                    break
            for j in range(25):
                pk_r += 1
                right_thresh = self.base_med_pe['sum']
                if a[pk_r]<=right_thresh or pk_r>=(len(a)-1):
                    break
            self.start[i] = pk_l
            self.end[i] = pk_r

    def calc_pulse_info(self):
        """
        Calculate pulse info, such as ex area, peak height, coincidence, etc.
        """
        if self.n_pulses<=0:
            return None

        # calcualte channel x pulse level variables (one per ch per pulse)
        # pulse area, height
        for ch in self.wfm.amp_pe.keys():
            a = self.wfm.amp_pe[ch]
            a_int = self.wfm.amp_pe_int[ch]
            self.area_pe[ch] = a_int[self.end]-a_int[self.start]
            self.height_pe[ch] = zeros(len(self.id))
            for i in self.id:
                start = self.start[i]
                end = self.end[i]
                self.height_pe[ch][i]=np.max(a[start:end])

        # calcualte pulse level variables (one per pulse)
        for i in self.id:
            coin = 0
            for ch, val in self.height_pe.items():
                if 'adc_' in ch:
                    if ch in self.cfg.non_signal_channels:
                        continue
                    if val>=self.cfg.coincidence_threshold_pe:
                        coin +=1
            SBA = (self.area_pe['sum_side'][i]-self.area_pe['sum_bt'][i])
            SBA = SBA / (self.area_pe['sum_side'][i]+self.area_pe['sum_bt'][i])
            self.sba =  SBA # side-to-bottom asymmetry
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

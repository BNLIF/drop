from numpy import array, zeros, sort, arange, ndarray, uint32, uint16, place, logical_and, argsort, argmax
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from waveform import Waveform
from yaml_reader import YamlReader, SAMPLE_TO_NS

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
        self.area_sum_pe = []
        self.area_bot_pe = []
        self.area_side_pe = []
        self.sba = [] # side-bottom-asymmetry
        self.ptime_ns = []
        self.coincidence = []
        self.area_max_frac = []
        self.area_max_ch_id = []

        self.area_ch_pe = []
        self.height_ch_pe = []
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

    def calc_pulse_ch_info(self):
        """
        Calculate pulse x channel variables.
        One per pulse per channel, excluding padles and summed channels.
        """
        if self.n_pulses<=0:
            return None

        # calcualte channel x pulse level variables (one per ch per pulse)
        # pulse area, height, coincidence
        for i in self.id:
            start = self.start[i] # start of pulse i in sample
            end = self.end[i] # end of pulse i in sample
            area_pe = {} # integral within start to end
            height_pe = {} # pulse height within start to end
            for ch in self.wfm.amp_pe.keys():
                a = self.wfm.amp_pe[ch]
                a_int = self.wfm.amp_pe_int[ch]
                area_pe[ch] = a_int[end]-a_int[start]
                height_pe[ch] = np.max(a[start:end])
            self.height_ch_pe.append(height_pe)
            self.area_ch_pe.append(area_pe)

    def calc_pulse_info(self):
        """
        Calculate pulse variable
        One per pulse
        """
        height_thresh = self.cfg.spe_height_threshold

        # calcualte pulse level variables (one per pulse)
        for i in self.id:
            start = self.start[i] # start of pulse i in sample
            end = self.end[i] # end of pulse i in sample
            a_sum = self.wfm.amp_pe['sum']
            a_sum_int = self.wfm.amp_pe_int['sum']
            a_bot = self.wfm.amp_pe['sum_bot']
            a_bot_int = self.wfm.amp_pe_int['sum_bot']
            a_side = self.wfm.amp_pe['sum_side']
            a_side_int = self.wfm.amp_pe_int['sum_side']
            self.area_sum_pe.append(a_sum_int[end]-a_sum_int[start])
            self.area_bot_pe.append(a_bot_int[end]-a_bot_int[start])
            self.area_side_pe.append(a_side_int[end]-a_side_int[start])
            self.ptime_ns.append(argmax(a_sum[start:end])*SAMPLE_TO_NS)
            sba = (self.area_side_pe[-1]-self.area_bot_pe[-1])/self.area_sum_pe[-1]
            self.sba.append( sba ) # side-to-bottom asymmetry

            area_max_frac = 0
            area_max_ch_id = 0
            coin=0
            for ch in self.wfm.amp_pe.keys():
                if ch[0:4]=='adc_':
                    a = self.wfm.amp_pe[ch]
                    a_int = self.wfm.amp_pe_int[ch]
                    area = a_int[end]-a_int[start]
                    if self.height_ch_pe[i][ch]>height_thresh:
                        coin += 1

                    if area>area_max_frac:
                        area_max_frac = area
                        ch_id = self.wfm.ch_name_to_id_dict[ch]
                        area_max_ch_id = ch_id
            area_max_frac /= self.area_sum_pe[-1]
            self.area_max_frac.append(area_max_frac)
            self.area_max_ch_id.append(area_max_ch_id)
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

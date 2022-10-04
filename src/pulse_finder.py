from numpy import array, zeros, sort, arange, ndarray, uint32, uint16, place, logical_and, argsort, argmax
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os
import sys
from waveform import Waveform
from yaml_reader import YamlReader, SAMPLE_TO_NS, MY_QUANTILES
sys.path.append(os.environ['LIB_DIR'])
from utilities import generate_colormap, digitial_butter_highpass_filter
import utilities_numba as util_nb

class PulseFinder():
    """
    Finding pulses.
    """
    def __init__(self, cfg: YamlReader, wfm: Waveform):
        """Constructor

        Pulse finder identify pulses in the sum channels. A pulse is defined by
        pulse_start and pulse_end sample index, and labelled by pulse_id. Once
        a pulse is found (or defined), pulse variables are then calculated.
        If scipy pulse finder is used, pulses are order in decending order of
        prominence.

        Args:
            cfg (YamlReader): configuration by YamlReader class
            wfm (Waveform): waveform by Waveform class
        """
        self.cfg = cfg
        self.reset()

    def reset(self):
        """
        Variables that needs to be reset per event

        Notes:
            If you want to add more pulse variables, do not forget to reset it
            here.
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
        self.area_row1_pe = []
        self.area_row2_pe = []
        self.area_row3_pe = []
        self.area_row4_pe = []
        self.area_col1_pe = []
        self.area_col2_pe = []
        self.area_col3_pe = []
        self.area_col4_pe = []
        self.area_user_pe = []
        self.aft10_sum_ns = []
        self.aft10_bot_ns = []
        self.aft10_side_ns = []
        self.aft10_row1_ns = []
        self.aft10_row2_ns = []
        self.aft10_row3_ns = []
        self.aft10_row4_ns = []
        self.height_sum_pe = []
        self.height_bot_pe = []
        self.height_side_pe = []
        self.sba = [] # side-bottom-asymmetry
        self.ptime_ns = []
        self.coincidence = []
        self.area_max_frac = []
        self.area_max_ch_id = []
        self.area_bot_max_frac = []
        self.area_bot_max_ch_id = []
        self.pulse_saturated = []

        self.area_ch_pe = []
        self.height_ch_pe = []
        self.wfm = None

    def scipy_find_peaks(self):
        """
        Scipy find_peaks functions. The parameters can be tuned in the yaml file.
        """
        pars = self.cfg.scipy_pf_pars
        self.base_med_pe = {}
        for ch, val in self.wfm.amp_pe.items():
            if 'adc_' in ch:
                continue
            if 'sum_col' in ch:
                continue
            if 'sum_row' in ch:
                continue
            a = self.wfm.amp_pe[ch]
            qx = util_nb.quantile_f8(a[0:200], MY_QUANTILES)
            std = abs(qx[2]-qx[0])
            med = qx[1]
            self.base_med_pe[ch] = med
            peaks, prop = find_peaks(a,
                distance=pars.distance,
                threshold=pars.threshold,
                height=pars.height,
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
        idx = argsort(self.peak_properties['sum']['prominences'])[::-1] # decending
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
            for j in range(42):
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

        TODO: these variables are calcualted but not yet saved.
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
                # height_pe[ch] = np.max(a[start:end])
                height_pe[ch] = util_nb.max(a[start:end])
            self.height_ch_pe.append(height_pe)
            self.area_ch_pe.append(area_pe)

    def calc_pulse_info(self):
        """
        Calculate pulse-level variables. One event may have many pulses.

        area: integral in unit of PE
        height: max height in unit of PE/ns
        ptime_ns: peak time in ns
        sba: side bottom asymmetry
        coincidence: number of PMTs whose pulse height pass threshold
        area_max_frac: fraction of light in max PMTs
        ... [add more if you wish]
        """
        t_ax = self.wfm.time_axis_ns
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
            a_row1 = self.wfm.amp_pe['sum_row1']
            a_row2 = self.wfm.amp_pe['sum_row2']
            a_row3 = self.wfm.amp_pe['sum_row3']
            a_row4 = self.wfm.amp_pe['sum_row4']
            a_row1_int = self.wfm.amp_pe_int['sum_row1']
            a_row2_int = self.wfm.amp_pe_int['sum_row2']
            a_row3_int = self.wfm.amp_pe_int['sum_row3']
            a_row4_int = self.wfm.amp_pe_int['sum_row4']
            a_col1 = self.wfm.amp_pe['sum_col1']
            a_col2 = self.wfm.amp_pe['sum_col2']
            a_col3 = self.wfm.amp_pe['sum_col3']
            a_col4 = self.wfm.amp_pe['sum_col4']
            a_col1_int = self.wfm.amp_pe_int['sum_col1']
            a_col2_int = self.wfm.amp_pe_int['sum_col2']
            a_col3_int = self.wfm.amp_pe_int['sum_col3']
            a_col4_int = self.wfm.amp_pe_int['sum_col4']
            a_user = self.wfm.amp_pe['sum_user']
            a_user_int = self.wfm.amp_pe_int['sum_user']
            self.area_sum_pe.append(a_sum_int[end]-a_sum_int[start])
            self.area_bot_pe.append(a_bot_int[end]-a_bot_int[start])
            self.area_side_pe.append(a_side_int[end]-a_side_int[start])
            self.area_row1_pe.append(a_row1_int[end]-a_row1_int[start])
            self.area_row2_pe.append(a_row2_int[end]-a_row2_int[start])
            self.area_row3_pe.append(a_row3_int[end]-a_row3_int[start])
            self.area_row4_pe.append(a_row4_int[end]-a_row4_int[start])
            self.area_col1_pe.append(a_col1_int[end]-a_col1_int[start])
            self.area_col2_pe.append(a_col2_int[end]-a_col2_int[start])
            self.area_col3_pe.append(a_col3_int[end]-a_col3_int[start])
            self.area_col4_pe.append(a_col4_int[end]-a_col4_int[start])
            self.area_user_pe.append(a_user_int[end]-a_user_int[start])
            self.aft10_sum_ns.append(util_nb.aft(t_ax[start:end], a_sum_int[start:end], 0.1))
            self.aft10_bot_ns.append(util_nb.aft(t_ax[start:end], a_bot_int[start:end], 0.1))
            self.aft10_side_ns.append(util_nb.aft(t_ax[start:end], a_side_int[start:end], 0.1))
            self.aft10_row1_ns.append(util_nb.aft(t_ax[start:end], a_row1_int[start:end], 0.1))
            self.aft10_row2_ns.append(util_nb.aft(t_ax[start:end], a_row2_int[start:end], 0.1))
            self.aft10_row3_ns.append(util_nb.aft(t_ax[start:end], a_row3_int[start:end], 0.1))
            self.aft10_row4_ns.append(util_nb.aft(t_ax[start:end], a_row4_int[start:end], 0.1))
            # self.height_sum_pe.append(np.max(a_sum[start:end]))
            # self.height_bot_pe.append(np.max(a_bot[start:end]))
            # self.height_side_pe.append(np.max(a_side[start:end]))
            self.height_sum_pe.append(util_nb.max(a_sum[start:end]))
            self.height_bot_pe.append(util_nb.max(a_bot[start:end]))
            self.height_side_pe.append(util_nb.max(a_side[start:end]))
            self.ptime_ns.append( (argmax(a_sum[start:end])+start)*SAMPLE_TO_NS )
            sba = (self.area_side_pe[-1]-self.area_bot_pe[-1])/self.area_sum_pe[-1]
            self.sba.append( sba ) # side-to-bottom asymmetry

            area_max_frac = 0
            area_max_ch_id = 0
            area_bot_max_frac = 0
            area_bot_max_ch_id = 0
            coin=0
            pulse_saturated = False
            for ch in self.wfm.amp_pe.keys():
                if ch[0:4]=='adc_':
                    a = self.wfm.amp_pe[ch]
                    a_int = self.wfm.amp_pe_int[ch]
                    area = a_int[end]-a_int[start]
                    if self.height_ch_pe[i][ch]>height_thresh:
                        coin += 1
                    if area>area_max_frac:
                        area_max_frac = area
                        area_max_ch_id = self.wfm.ch_name_to_id_dict[ch]
                    if ch in self.cfg.bottom_pmt_channels and area>area_bot_max_frac:
                        area_bot_max_frac = area
                        area_bot_max_ch_id = self.wfm.ch_name_to_id_dict[ch]
                    if self.wfm.ch_saturated[ch]:
                        val = self.wfm.raw_data[ch][start:end]
                        if val.min()<=self.cfg.ch_saturated_threshold:
                            pulse_saturated=True
            area_max_frac /= self.area_sum_pe[-1]
            self.area_max_frac.append(area_max_frac)
            self.area_max_ch_id.append(area_max_ch_id)
            self.area_bot_max_frac.append(area_bot_max_frac)
            self.area_bot_max_ch_id.append(area_bot_max_ch_id)
            self.coincidence.append(coin)
            self.pulse_saturated.append(pulse_saturated)
        return None


    def is_spe(self, ch='sum') -> bool:
        """ Work in Progress """
        pass

    def display(self, ch='sum'):
        '''
        A plotting function showcase pulse finder.

        Args:
            ch (str, list):  specified a channel to dispaly.
                ex. b1_ch0, ['b1_ch0', 'b1_ch1']. Default: sum

        Notes:
            depricated? At least X.X. does not recall using it recently.
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

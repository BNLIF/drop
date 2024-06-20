'''
One waveform per event.

Outline
- baseline subtraction per channel
- pulse finding
- sum channels
'''
from numpy import zeros, argwhere, trapz, diff, sign, concatenate, quantile, argmax
from numpy import median, cumsum
import numpy as np
import matplotlib.pylab as plt
from matplotlib import cm
import os
import sys
sys.path.append(os.environ['LIB_DIR'])
import utilities_numba as util_nb
from yaml_reader import YamlReader, SAMPLE_TO_NS, MY_QUANTILES
from utilities import generate_colormap, digitial_butter_highpass_filter

class Waveform():
    """
    Waveform class. One waveform per event.
    """
    def __init__(self, cfg: YamlReader):
        """Constructor.

        Args:
            cfg (YamlReader): the config objection from YamlReader class.
        """
        if cfg is not None:
            self.cfg = cfg
        self.ch_names = None
        self.ch_id = None
        self.ch_name_to_id_dict= None
        self.n_boards = None
        self.spe_mean = None
        self.reset()
        return None

    def reset(self):
        """
        Variables that needs to be reset from event to event
        """
        # from raw data
        self.raw_data = None

        # amplitude is baseline subtracted waveform, in unit of mV or PE
        self.amp_mV ={}
        self.amp_pe={}
        self.amp_pe_int={} # accumulated (integrated) waveform, PE

        # calculated baseline
        self.flat_base_mV = {}
        self.flat_base_std_mV = {}
        self.flat_base_pe = {}
        self.flat_base_std_pe = {}
        self.ma_base_pe = {} # moving average mean
        self.ma_base_std_pe = {} # moving average std

    def set_raw_data(self, val):
        """
        Set raw data.
        """
        self.raw_data = {}
        for ch in self.ch_names:
            self.raw_data[ch] = val[ch].to_numpy() # numpy is faster
        self.event_id = val.event_id
        self.event_ttt = val.event_ttt
        self.event_sanity=val.event_sanity

    def find_saturation(self):
        """
        Saturation is easily defined in the raw waveform in adc. Since signal
        are negatively polarized, a channel is saturated if it cross below 0 adc.
        - Flag a channel if it's saturated.
        - Flag a event if any of the signal channels are saturated.
        """
        thresh = self.cfg.ch_saturated_threshold #
        self.ch_saturated = {}
        self.event_saturated = False
        for ch in self.ch_names:
            val = self.raw_data[ch]
            if val.min()<=thresh:
                self.ch_saturated[ch]=True
                if ch in self.cfg.non_signal_channels:
                    continue
                self.event_saturated = True
            else:
                self.ch_saturated[ch]=False
        return None

    def define_trigger_position(self):
        """
        You have to define an event's trigger time. For simplicity, use time of
        the first trigger arrived at the master board. This is calculate based
        on DAQ length and post_trigger fraction.
        """
        if self.cfg.daisy_chain:
            for ch in self.ch_names:
                if '_b1' in ch:
                    n_samp = len(self.amp_mV[ch])
                    pre_trg_frac = 1.0-self.cfg.post_trigger
                    self.trg_pos = int(n_samp*pre_trg_frac)
                    self.trg_time_ns = self.trg_pos*(SAMPLE_TO_NS)
                    return None
        else:
            print('Sorry pal. Fan-out not yet implemented.')

    def get_flat_baseline(self, val, summed_channel=False):
        """
        Define a flat baseline. Find the median and std, and return them

        Args:
            val: array of float

        Return:
            float, float
        """
        # qx = np.quantile(val, MY_QUANTILES)
        if summed_channel:
            qx = util_nb.quantile_f8(val, MY_QUANTILES)
        else:
            qx = util_nb.quantile_u2(val, MY_QUANTILES)
        return qx[1], abs(qx[2]-qx[0])/2

    def subtract_flat_baseline(self):
        """
        Very basic: subratct a flat baseline for all channels. New variables
        are saved in class for later usage: flat_base_mV, flat_base_std_mV,
        amp_mV.
        """
        if self.ch_names is None:
            sys.exit('ERROR: Waveform::ch_names is not specified.')

        adc_to_mV = self.cfg.dgtz_dynamic_range_mV/(2**14-1)
        for ch in self.ch_names:
            val = self.raw_data[ch]
            med, std = self.get_flat_baseline(val)
            self.flat_base_mV[ch] = med # save a copy
            self.flat_base_std_mV[ch] = std # save a copy
            amp = -(val-med)
            if self.cfg.apply_high_pass_filter:
                cutoff_Hz = self.cfg.high_pass_cutoff_Hz
                amp = digitial_butter_highpass_filter(amp, cutoff_Hz)
            self.amp_mV[ch] = amp*adc_to_mV
        return None

    def do_spe_normalization(self):
        """
        Do SPE normalization for all signal channels
        Muon paddle is considered non-signal channel, and hence not SPE normalized
        """
        if self.spe_mean is None:
            sys.exit('ERROR: spe_mean not specified in Waveform. Unable to normalized.')

        for ch, val in self.amp_mV.items():
            if ch in self.cfg.non_signal_channels:
                continue
            spe_mean = self.spe_mean[ch]
            self.amp_pe[ch] = val/50/spe_mean
            self.flat_base_pe[ch] = self.flat_base_mV[ch]/50/spe_mean
            self.flat_base_std_pe[ch] = self.flat_base_std_mV[ch]/50/spe_mean
        return None

    def correct_daisy_chain_trg_delay(self):
        """
        Shift a channel's waveform based on which board it is. The 48 ns delay
        from V1730s trg_in to trg_out is calibrated with a square pulse. We do
        not expect it changes. Hence hard coded below.

        Remember to shift trigger position too.

        TODO:
            1. save the delay in config yaml file.
            2. what about FAN-OUT?

        Notes:
            boardId is baked into ch_name.
        """
        dT_ns = 48 # externally calibrated parameter
        dS = dT_ns//int(SAMPLE_TO_NS)
        for ch, a in self.amp_pe.items():
            a_corr = a.copy()
            if "_b1" in ch:
                a_corr=a[dS*2:]
            elif "_b2" in ch:
                a_corr=a[dS:-dS]
            elif ("_b3" in ch) or ("_b4" in ch):
                a_corr=a[0:-dS*2]
            else:
                print("ERROR in correct_trg_delay: invalid boardId")
                return None
            self.amp_pe[ch] = a_corr
        self.trg_pos -= dS*2
        self.trg_time_ns -= dT_ns*2

    def sum_channels(self):
        """
        Sum up channels.
            - "sum" means the sum of all PMTs
            - "bot" means the sum of all bottom PMTs
            - "side" means the sum of all side PMTs
            - 'user' means a user-defined list.
            - all in skip are skipped.
        """
        tot_pe = 0
        bt_pe = 0
        ir_pe = 0
        side_pe=0
        r1_pe, r2_pe, r3_pe, r4_pe = 0, 0, 0, 0
        c1_pe, c2_pe, c3_pe, c4_pe, c5_pe, c6_pe = 0, 0, 0, 0, 0, 0
        user_pe = 0
        for ch, val in self.amp_pe.items():
            print(f"Channel: {ch}, Length: {len(val)}")
            if 'adc_' in ch:
                if ch in self.cfg.skip_pmt_channels:
                    continue
                tot_pe += val
                if ch in self.cfg.bottom_pmt_channels:
                    bt_pe += val
                if ch in self.cfg.side_pmt_channels:
                    side_pe += val
                if ch in self.cfg.row1_pmt_channels:
                    r1_pe += val
                if ch in self.cfg.row2_pmt_channels:
                    r2_pe += val
                if ch in self.cfg.row3_pmt_channels:
                    r3_pe += val
                if ch in self.cfg.row4_pmt_channels:
                    r4_pe += val
                #if ch in self.cfg.row5_pmt_channels:
                #    r5_pe += val
                #if ch in self.cfg.row6_pmt_channels:
                #    r6_pe += val
                #if ch in self.cfg.row7_pmt_channels:
                #    r7_pe += val
                if ch in self.cfg.col1_pmt_channels:
                    c1_pe += val
                if ch in self.cfg.col2_pmt_channels:
                    c2_pe += val
                if ch in self.cfg.col3_pmt_channels:
                    c3_pe += val
                if ch in self.cfg.col4_pmt_channels:
                    c4_pe += val
                if ch in self.cfg.col5_pmt_channels:
                    c5_pe += val
                if ch in self.cfg.col6_pmt_channels:
                    c6_pe += val
                #if ch in self.cfg.col7_pmt_channels:
                #    c7_pe += val
                #if ch in self.cfg.col8_pmt_channels:
                #    c8_pe += val
                if ch in self.cfg.user_pmt_channels:
                    user_pe += val
        self.amp_pe['sum'] = tot_pe
        med, std = self.get_flat_baseline(tot_pe, summed_channel=True)
        self.flat_base_pe['sum'] = med
        self.flat_base_std_pe['sum'] = std
        self.amp_pe['sum_bot'] = bt_pe
        self.amp_pe['sum_side'] = side_pe
        self.amp_pe['sum_row1'] = r1_pe
        self.amp_pe['sum_row2'] = r2_pe
        self.amp_pe['sum_row3'] = r3_pe
        self.amp_pe['sum_row4'] = r4_pe
        #self.amp_pe['sum_row5'] = r5_pe
        #self.amp_pe['sum_row6'] = r6_pe
        #self.amp_pe['sum_row7'] = r7_pe
        self.amp_pe['sum_col1'] = c1_pe
        self.amp_pe['sum_col2'] = c2_pe
        self.amp_pe['sum_col3'] = c3_pe
        self.amp_pe['sum_col4'] = c4_pe
        self.amp_pe['sum_col5'] = c5_pe
        self.amp_pe['sum_col6'] = c6_pe
        #self.amp_pe['sum_col7'] = c7_pe
        #self.amp_pe['sum_col8'] = c8_pe
        self.amp_pe['sum_user'] = user_pe
        return None

    def define_time_axis(self):
        """
        This is the time axis after daisy chain correction
        Not often use
        """
        n_samp = len(self.amp_pe['sum'])
        t=np.linspace(0, (n_samp-1)*SAMPLE_TO_NS, n_samp)
        self.time_axis_ns = t
        self.n_samp = n_samp

    def integrate_waveform(self):
        """
        Compute accumulated integral of the waveform. Do not forget to multiple by
        the sample size (2ns for V1730s) as it's integral not accumulated sum.
        """
        for ch, val in self.amp_pe.items():
            self.amp_pe_int[ch] = cumsum(val)*(SAMPLE_TO_NS) # adc*ns

    def find_ma_baseline(self):
        n = self.cfg.moving_avg_length
        win = np.ones(n)
        for ch in self.ch_names:
            a = self.amp_mV
            ma =  np.convolve(a, win/n, mode='valid')
            base = np.concatenate(([val[k] for k in range(n-1)],ma))
            std = np.std(a - base) # std after subtraction
            self.ma_base_pe[ch]=base.copy()
            self.ma_base_std_pe[ch] = std # bs stands for baseline subtracted
        return None

    def calc_roi_info(self):
        """
        Calculate variables within a region of interest (ROI) -- ROI an interval
        whose start_ns and end_ns are defined in yaml config file

        The following info are calculated:
        - area, in unit of PE
        - height, in unit of PE/ns
        - low, in uint of PE/ns
        - std, in unit of PE/ns and mV
        """
        self.roi_area_pe=[]
        self.roi_height_pe=[]
        self.roi_low_pe=[]
        self.roi_std_pe=[]
        self.roi_std_mV=[]
        for i in range(len(self.cfg.roi_start_ns)):
            start= self.trg_pos + (self.cfg.roi_start_ns[i]//int(SAMPLE_TO_NS))
            end= self.trg_pos + (self.cfg.roi_end_ns[i]//int(SAMPLE_TO_NS))
            start=max(0, start)
            end = min(self.n_samp-1, end)
            height_pe={}
            area_pe = {}
            low_pe = {}
            std_pe = {}
            std_mV = {}
            for ch, a in self.amp_pe.items():
                if ch[0:4]!='adc_':
                    continue
                height_pe[ch] = util_nb.max(a[start:end])
                low_pe[ch] = util_nb.min(a[start:end])
                std_pe[ch] = util_nb.std(a[start:end])
                std_mV[ch] = std_pe[ch]*50*self.spe_mean[ch]
                a_int =  self.amp_pe_int[ch]
                area_pe[ch] = a_int[end]-a_int[start]
            self.roi_height_pe.append(height_pe)
            self.roi_area_pe.append(area_pe)
            self.roi_low_pe.append(low_pe)
            self.roi_std_pe.append(std_pe)
            self.roi_std_mV.append(std_mV)
        return None

    def calc_aux_ch_info(self):
        """
        Reconstruct simple variables for non-signal channels (auxiliary channel)
        For example, the paddles are non-signal channels that provides auxiliary info
        """
        self.aux_ch_area_mV={}
        for ch in self.cfg.non_signal_channels:
            a=self.amp_mV[ch]
            pp = argmax(a) # peak position
            start=np.max([pp-50, 0])
            end = np.min([pp+50, len(a)-1])
            area = np.sum(a[start:end])*SAMPLE_TO_NS
            self.aux_ch_area_mV[ch] = area
        return None

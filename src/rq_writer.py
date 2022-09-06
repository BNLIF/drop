from numpy import int16, int32, uint16, uint32, float32, array, zeros
import numpy as np
import uproot
import awkward as ak
from os.path import splitext, basename, dirname
#import h5py

from pulse_finder import PulseFinder
from waveform import Waveform
from pandas import DataFrame

class RQWriter:
    """
    Write to file
    """
    def __init__(self, args, n_pmt_ch, n_aux_ch, basket_size=1000):
        """
        Constructor: create root tree structure, fill, and write. The n_ch and
        n_aux_ch variables are needed to define branch structure (static array).
        Pulse-level variables are dynamic arrays, hence no need to define array
        size. Dynamic array is slower than static array.

        Args:
            args: input arguments passed to main, it includes output Directory
            n_ch: number of channels used for PMTs (n_active_ch - n_aux_ch)
            n_aux_ch: number of auxiliary (not-signal) channels
            batch_size: number of entries per batch
        """

        self.args = args
        self.n_pmt_ch = n_pmt_ch
        self.n_aux_ch = n_aux_ch
        self.basket_size = basket_size
        self.init_basket_cap = 100
        if self.basket_size<=10:
            print("Info: write small baskets is not recommended by Jim \
            Pivarski. Code may be slow this way. Rule of thumb: at least \
            100 kb/basket/branch. See: \
            https://github.com/scikit-hep/uproot4/pull/428")
        self.reset()

    def reset(self):
        """
        Variables that needs to be reset per batch of events
        """
        # Event level variable
        self.event_id=[]
        self.event_ttt=[]
        self.event_sanity=[]

        # pmt channel level variables
        self.ch_id = [] # boardId*100 + chID
        self.ch_roi0_height_pe = []
        self.ch_roi1_height_pe = []
        self.ch_roi2_height_pe = []
        self.ch_roi0_area_pe = []
        self.ch_roi1_area_pe = []
        self.ch_roi2_area_pe = []

        # non-signal channel info (auxiliary channels)
        self.aux_ch_id = []
        self.aux_ch_area_mV = []

        # pulse level variables
        self.n_pulses=[]
        self.pulse_id = []
        self.pulse_start = []
        self.pulse_end = []
        self.pulse_area_sum_pe = []
        self.pulse_area_bot_pe = []
        self.pulse_area_side_pe = []
        self.pulse_height_sum_pe = []
        self.pulse_height_bot_pe = []
        self.pulse_height_side_pe = []
        self.pulse_sba = []
        self.pulse_ptime_ns = []
        self.pulse_coincidence = []
        self.pulse_area_max_frac = []
        self.pulse_area_max_ch_id = []

        # channel x pulse variables (not yet implemented)
        self.pulse_ch_area_pe = []
        self.pulse_ch_height_pe = []
        return None

    def create_output(self):
        """
        First create output file name based on input file names
        Then create empty tree via mktree
        """
        self.output_dir = str(self.args.output_dir)
        if self.output_dir=="":
            self.output_dir = dirname(self.args.if_path)
        fname = basename(self.args.if_path)
        name, f_ext = splitext(fname)
        self.of_path = self.output_dir + '/' + name +'_rq.root'
        self.file = uproot.recreate(self.of_path)

        bs = self.basket_size
        type_ch_uint16 = ak.Array(zeros([bs, self.n_pmt_ch], dtype=uint16)).type
        type_ch_float = ak.Array(zeros([bs, self.n_pmt_ch], dtype=float32)).type
        type_aux_ch_uint16 = ak.Array(zeros([bs, self.n_aux_ch], dtype=uint16)).type
        type_aux_ch_float = ak.Array(zeros([bs, self.n_aux_ch], dtype=float32)).type

        type_event={
            'event_id': 'uint32',
            'event_ttt': 'uint64',
            'event_sanity': 'uint32',

            'ch_id': type_ch_uint16,
            'ch_roi0_height_pe': type_ch_float,
            'ch_roi1_height_pe': type_ch_float,
            'ch_roi2_height_pe': type_ch_float,
            'ch_roi0_area_pe': type_ch_float,
            'ch_roi1_area_pe': type_ch_float,
            'ch_roi2_area_pe': type_ch_float,

            'aux_ch_id': type_aux_ch_uint16,
            'aux_ch_area_mV': type_aux_ch_float,
        }

        type_uint = ak.values_astype([[0], []], uint32)
        type_float = ak.values_astype([[0.], []], float32)
        type_pulse={
            'id': type_uint,
            'start': type_uint,
            'end': type_uint,
            'area_sum_pe': type_float,
            'area_bot_pe': type_float,
            'area_side_pe': type_float,
            'height_sum_pe': type_float,
            'height_bot_pe': type_float,
            'height_side_pe': type_float,
            'sba': type_float,
            'ptime_ns': type_float,
            'coincidence': type_uint,
            'area_max_frac': type_float,
            'area_max_ch_id': type_uint,
        }
        type_event['pulse']=ak.zip(type_pulse).type

        #a=ak.values_astype(a, np.uint16)
        self.file.mktree('event', type_event,
                         initial_basket_capacity=self.init_basket_cap)
        print('\nInfo: creating tree structure as the following: ')
        self.file['event'].show()
        return None

    def fill(self, wfm: Waveform, pf: PulseFinder):
        """
        Add variables to the basket. Append one event at a time.

        Args:
            wfm (Waveform): waveform from Waveform class.
            pf (PulseFinder): from PulseFinder class

        Notes:
            The small but growing list of data types can be written as TTrees:
                * dict of NumPy arrays
                * Single numpy array
                * Awkward Array containing one level of variable length
                * a single Pandas DataFrame

        So a list of numpy array is not an acceptable format. A list of
        list, on the other hand, is okay because it can be casted into
        a awkward array at extend stage. Hence, call tolist() below. I
        hope there is a better solution.
        https://uproot.readthedocs.io/en/latest/basic.html
        """
        # event level
        self.event_id.append(wfm.event_id)
        self.event_ttt.append(wfm.event_ttt)
        self.event_sanity.append(wfm.event_sanity)

        # channel level
        n_ch = len(wfm.ch_id)-self.n_aux_ch
        if n_ch != self.n_pmt_ch:
            print('wfm.event_id=', wfm.event_id)
            msg = "ERROR: len(wfm.ch_id)=%d while n_aux_ch=%d, but n_ch=%d" % (len(wfm.ch_id), self.n_aux_ch , n_ch)
            sys.exit(msg)
        ch_id = zeros(n_ch)
        roi0_h = zeros(n_ch)
        roi1_h = zeros(n_ch)
        roi2_h = zeros(n_ch)
        roi0_a = zeros(n_ch)
        roi1_a = zeros(n_ch)
        roi2_a = zeros(n_ch)
        i=0
        for ch in wfm.ch_names:
            if ch in wfm.cfg.non_signal_channels:
                continue
            ch_id[i] = wfm.ch_name_to_id_dict[ch]
            roi0_h[i] = wfm.roi_height_pe[0][ch]
            roi1_h[i] = wfm.roi_height_pe[1][ch]
            roi2_h[i] = wfm.roi_height_pe[2][ch]
            roi0_a[i] = wfm.roi_area_pe[0][ch]
            roi1_a[i] = wfm.roi_area_pe[1][ch]
            roi2_a[i] = wfm.roi_area_pe[2][ch]
            i+=1
        self.ch_id.append( ch_id )
        self.ch_roi0_height_pe.append(roi0_h)
        self.ch_roi1_height_pe.append(roi1_h)
        self.ch_roi2_height_pe.append(roi2_h)
        self.ch_roi0_area_pe.append(roi0_a)
        self.ch_roi1_area_pe.append(roi1_a)
        self.ch_roi2_area_pe.append(roi2_a)

        # auxiliary channel
        n_aux_ch = len(wfm.cfg.non_signal_channels)
        aux_ch_id = zeros(n_aux_ch)
        aux_ch_area_mV = zeros(n_aux_ch)
        for i in range(n_aux_ch):
            ch = wfm.cfg.non_signal_channels[i]
            aux_ch_id[i] = wfm.ch_name_to_id_dict[ch]
            aux_ch_area_mV[i] = wfm.aux_ch_area_mV[ch]
        self.aux_ch_id.append(aux_ch_id)
        self.aux_ch_area_mV.append(aux_ch_area_mV)

        # pulse level
        self.n_pulses.append(pf.n_pulses)
        self.pulse_id.append(pf.id)
        self.pulse_start.append(pf.start)
        self.pulse_end.append(pf.end)
        self.pulse_area_sum_pe.append(pf.area_sum_pe)
        self.pulse_area_bot_pe.append(pf.area_bot_pe)
        self.pulse_area_side_pe.append(pf.area_side_pe)
        self.pulse_height_sum_pe.append(pf.height_sum_pe)
        self.pulse_height_bot_pe.append(pf.height_bot_pe)
        self.pulse_height_side_pe.append(pf.height_side_pe)
        self.pulse_sba.append(pf.sba)
        self.pulse_ptime_ns.append(pf.ptime_ns)
        self.pulse_coincidence.append(pf.coincidence)
        self.pulse_area_max_frac.append(pf.area_max_frac)
        self.pulse_area_max_ch_id.append(pf.area_max_ch_id)

        # pulse x channel level
        # self.pulse_area_pe.append(pf.area_pe.tolist()) # actually adc*ns
        # self.pulse_height_pe.append(pf.height_pe)

        return None

    def close(self):
        """
        remember to close file after done
        """
        self.file.close()

    def dump_run_rq(self, rq: dict):
        """
        Write one per run/file. No need to loop.
        """
        rq['n_pmt_ch']=[self.n_pmt_ch]
        rq['n_aux_ch']=[self.n_aux_ch]
        self.file['run_info'] = rq

    def dump_pmt_info(self, df: DataFrame):
        """
        uproot only accept dictionary
        """
        if df is None:
            return None

        df = df.astype({
            "ch_id": uint16,
            "spe_mean": float32,
            "spe_width": float32,
            "spe_mean_err": float32,
            "spe_width_err": float32,
            "dof": uint16,
            "HV": int16,
        })

        pmt_info = {
            'ch_id': df['ch_id'].tolist(),
            #'pmt_name': df['pmt_name'].tolist(), # uproot write does not handle string well
            'spe_mean': df['spe_mean'].tolist(),
            'spe_width': df['spe_width'].tolist(),
            'spe_mean_err': df['spe_mean_err'].tolist(),
            'spe_width_err': df['spe_width_err'].tolist(),
            'chi2': df['chi2'].tolist(),
            'dof': df['dof'].tolist(),
            'HV': df['HV'].tolist(),
        }
        self.file['pmt_info']=pmt_info

    def dump_event_rq(self):
        """
        Write one basket at a time
        """
        if not self.n_pulses:
            print("WARNING: Empty list. Nothing to dump")
            return None

        data_event = {
            "event_id": self.event_id,
            "event_ttt": self.event_ttt,
            'event_sanity': self.event_sanity,

            'ch_id': self.ch_id,
            'ch_roi0_height_pe': self.ch_roi0_height_pe,
            'ch_roi1_height_pe': self.ch_roi1_height_pe,
            'ch_roi2_height_pe': self.ch_roi2_height_pe,
            'ch_roi0_area_pe': self.ch_roi0_area_pe,
            'ch_roi1_area_pe': self.ch_roi1_area_pe,
            'ch_roi2_area_pe': self.ch_roi2_area_pe,

            'aux_ch_id': self.aux_ch_id,
            'aux_ch_area_mV': self.aux_ch_area_mV
        }

        data_pulse = {
            'id': self.pulse_id,
            'start': self.pulse_start,
            'end': self.pulse_end,
            'area_sum_pe': self.pulse_area_sum_pe,
            'area_bot_pe': self.pulse_area_bot_pe,
            'area_side_pe': self.pulse_area_side_pe,
            'height_sum_pe': self.pulse_height_sum_pe,
            'height_bot_pe': self.pulse_height_bot_pe,
            'height_side_pe': self.pulse_height_side_pe,
            'sba': self.pulse_sba,
            'ptime_ns': self.pulse_ptime_ns,
            'coincidence': self.pulse_coincidence,
            'area_max_frac': self.pulse_area_max_frac,
            'area_max_ch_id': self.pulse_area_max_ch_id,
        }
        data_event['pulse']=ak.zip(data_pulse)

        self.file['event'].extend(data_event)
        return None

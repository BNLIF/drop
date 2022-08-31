from numpy import int32, uint16, uint32, float32, array, zeros
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
    def __init__(self, args, basket_size=1000):
        self.args = args
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

        # channel level variables
        self.ch_id = [] # boardId*100 + chID
        self.roi0_height_pe = []
        self.roi1_height_pe = []
        self.roi2_height_pe = []
        self.roi0_area_pe = []
        self.roi1_area_pe = []
        self.roi2_area_pe = []

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


        # channel x pulse variables
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

        type_uint = ak.values_astype([[0], []], uint32)
        type_float = ak.values_astype([[0.], []], float32)

        pulse_info = {
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
        ch_info = {
            'id': type_uint,
            'roi0_height_pe': type_float,
            'roi1_height_pe': type_float,
            'roi2_height_pe': type_float,
            'roi0_area_pe': type_float,
            'roi1_area_pe': type_float,
            'roi2_area_pe': type_float,

        }
        ch_type = ak.zip(ch_info).type
        pulse_type= ak.zip(pulse_info).type

        #a=ak.values_astype(a, np.uint16)
        self.file.mktree('event', { 'event_id': 'uint32', 'event_ttt': 'uint32',
                                    'ch' : ch_type,
                                    'pulse': pulse_type},
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

        # channel level
        self.ch_id.append( wfm.ch_id )
        roi0_h = zeros(len(wfm.ch_id))
        roi1_h = zeros(len(wfm.ch_id))
        roi2_h = zeros(len(wfm.ch_id))
        roi0_a = zeros(len(wfm.ch_id))
        roi1_a = zeros(len(wfm.ch_id))
        roi2_a = zeros(len(wfm.ch_id))
        for i, ch_id in enumerate(wfm.ch_id):
            ch = "adc_b%d_ch%d" % (ch_id // 100, ch_id % 100)
            if ch in wfm.cfg.non_signal_channels:
                continue
            roi0_h[i] = wfm.roi_height_pe[0][ch]
            roi1_h[i] = wfm.roi_height_pe[1][ch]
            roi2_h[i] = wfm.roi_height_pe[2][ch]
            roi0_a[i] = wfm.roi_area_pe[0][ch]
            roi1_a[i] = wfm.roi_area_pe[1][ch]
            roi2_a[i] = wfm.roi_area_pe[2][ch]
        self.roi0_height_pe.append(roi0_h)
        self.roi1_height_pe.append(roi1_h)
        self.roi2_height_pe.append(roi2_h)
        self.roi0_area_pe.append(roi0_a)
        self.roi1_area_pe.append(roi1_a)
        self.roi2_area_pe.append(roi2_a)

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
        self.file['run_info'] = rq

    def dump_pmt_info(self, df: DataFrame):
        """
        uproot only accept dictionary
        """
        if df is None:
            return None

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
        pulse_info = {
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
        ch_info = {
            'id': self.ch_id,
            'roi0_height_pe': self.roi0_height_pe,
            'roi1_height_pe': self.roi1_height_pe,
            'roi2_height_pe': self.roi2_height_pe,
            'roi0_area_pe': self.roi0_area_pe,
            'roi1_area_pe': self.roi1_area_pe,
            'roi2_area_pe': self.roi2_area_pe,

        }
        data = {
            "event_id": self.event_id,
            "event_ttt": self.event_ttt,
            'ch': ak.zip(ch_info),
            'pulse': ak.zip(pulse_info)
        }
        self.file['event'].extend(data)
        return None

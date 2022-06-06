from numpy import int32, uint16, uint32, float32, array, zeros
import numpy as np
import uproot
import awkward as ak
from os.path import splitext, basename, dirname
#import h5py

from pulse_finder import PulseFinder
from waveform import Waveform

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
        self.roi0_height_adc = []
        self.roi1_height_adc = []
        self.roi2_height_adc = []
        self.roi0_area_adc = []
        self.roi1_area_adc = []
        self.roi2_area_adc = []


        # PulseFinder variables
        self.n_pulses=[]
        self.pulse_id = []
        self.pulse_start = []
        self.pulse_end = []
        self.pulse_area_adc = []
        self.pulse_height_adc = []
        self.pulse_coincidence = []
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

        type_uint = ak.values_astype([[0,0], []], uint32)
        type_float = ak.values_astype([[0.,0.], []], float32)
        pulse_info = {
        'id': type_uint,
        'start': type_uint,
        'end': type_uint,
        'area_adc': type_float,
        'height_adc': type_float,
        'coincidence': type_uint
        }
        ch_info = {
            'id': type_uint,
            'roi0_height_adc': type_float,
            'roi1_height_adc': type_float,
            'roi2_height_adc': type_float,
            'roi0_area_adc': type_float,
            'roi1_area_adc': type_float,
            'roi2_height_adc': type_float,

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
            ch_name = "adc_b%d_ch%d" % (ch_id // 100, ch_id % 100)
            roi0_h[i] = wfm.roi_height_adc[0][ch_name]
            roi1_h[i] = wfm.roi_height_adc[1][ch_name]
            roi2_h[i] = wfm.roi_height_adc[2][ch_name]
            roi0_a[i] = wfm.roi_area_adc[0][ch_name]
            roi1_a[i] = wfm.roi_area_adc[1][ch_name]
            roi2_a[i] = wfm.roi_area_adc[2][ch_name]

        self.roi0_height_adc.append(roi0_h)
        self.roi1_height_adc.append(roi1_h)
        self.roi2_height_adc.append(roi2_h)
        self.roi0_area_adc.append(roi0_a)
        self.roi1_area_adc.append(roi1_a)
        self.roi2_area_adc.append(roi2_a)

        # pulse level
        self.n_pulses.append(pf.n_pulses)
        self.pulse_id.append(pf.id.tolist())
        self.pulse_start.append(pf.start.tolist())
        self.pulse_end.append(pf.end.tolist())
        self.pulse_area_adc.append(pf.area_adc.tolist()) # actually adc*ns
        self.pulse_height_adc.append(pf.height_adc)
        self.pulse_coincidence.append(pf.coincidence)

        # pulse x channel level
        # <Work in Progress>
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
        'area_adc': self.pulse_area_adc,
        'height_adc': self.pulse_height_adc,
        'coincidence': self.pulse_coincidence
        }
        ch_info = {
            'id': self.ch_id,
            'roi0_height_adc': self.roi0_height_adc,
            'roi1_height_adc': self.roi1_height_adc,
            'roi2_height_adc': self.roi2_height_adc,
            'roi0_area_adc': self.roi0_area_adc,
            'roi1_area_adc': self.roi1_area_adc,
            'roi2_area_adc': self.roi2_area_adc,

        }
        data = {
            "event_id": self.event_id,
            "event_ttt": self.event_ttt,
            'ch': ak.zip(ch_info),
            'pulse': ak.zip(pulse_info)
        }
        self.file['event'].extend(data)
        return None

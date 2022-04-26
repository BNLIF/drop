from numpy import int32, uint16, uint32, float32, array, zeros
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
        # Waveform variables
        self.event_id=[]
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
        pulse = {
        'id': type_uint,
        'start': type_uint,
        'end': type_uint,
        'area_adc': type_float,
        'height_adc': type_float,
        'coincidence': type_uint
        }
        pulse= ak.zip(pulse)
        #a=ak.values_astype(a, np.uint16)
        self.file.mktree('event', {'pulse': pulse.type, 'event_id': 'uint32'})
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
        self.event_id.append(wfm.event_id)

        self.n_pulses.append(pf.n_pulses)
        self.pulse_id.append(pf.id.tolist())
        self.pulse_start.append(pf.start.tolist())
        self.pulse_end.append(pf.end.tolist())
        self.pulse_area_adc.append(pf.area_adc.tolist()) # actually adc*ns
        self.pulse_height_adc.append(pf.height_adc)
        self.pulse_coincidence.append(pf.coincidence)
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

        pulse = {
        'id': self.pulse_id,
        'start': self.pulse_start,
        'end': self.pulse_end,
        'area_adc': self.pulse_area_adc,
        'height_adc': self.pulse_height_adc,
        'coincidence': self.pulse_coincidence
        }
        self.file['event'].extend({
            "event_id": self.event_id,
            'pulse': ak.zip(pulse)
        })
        return None

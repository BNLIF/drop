"""
File options include: root, HDF5h5py

I will start with saving root format
"""

from numpy import int32, uint16, uint32, array
import uproot
import awkward as ak
from os.path import splitext
#import h5py

from pulse_finder import PulseFinder
from waveform import Waveform


class EventRQBasket:
    """
    Define a basket to hold all RQ variables for event tree
    """
    def __init__(self):
        self.reset()

    def reset(self):
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
        # keep track of basket size
        self.size = 0

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
        self.size +=1


class RQWriter:
    """
    Write to file
    """
    def __init__(self, config: dict, args):
        self.output_dir = config['output_dir']
        self.basket_size = uint32(config['basket_size'])

        if self.basket_size<=100:
            print("Info: write small baskets is not recommended by Jim \
            Pivarski. Code may be slow this way. Rule of thumb: at least \
            100 kb/basket/branch. See: \
            https://github.com/scikit-hep/uproot4/pull/428")
        if args.of=="":
            # create one from input file name
            f_path, f_ext = splitext(args.if_path)
            self.of_path = f_path+'.root'
        else:
            # use user specified filename
            self.of_path = self.output_dir + '/' + args.of
        self.create_output()

    def create_output(self):
        """
        Create output file and set up data structure
        """
        _, f_ext = splitext(self.of_path)
        if f_ext=='.root':
            self.file = uproot.recreate(self.of_path)
            self.file.mktree("event", {
                "event_id": "uint32",
                "n_pulses": "uint32",
                "pulse_id": "var * uint32",
                "pulse_start": "var * int32",
                "pulse_end": "var * int32",
                "pulse_area_adc": "var*float32",
                "pulse_height_adc": "var*float32",
                "pulse_coincidence": "var*uint32"
            })
        else:
            sys.exit('Sorry, requested output file format is not yet implmented.')

    def close(self):
        """
        remeber to close file after done
        """
        self.file.close()

    def write_run_rq(self, rq: dict):
        """
        Write one per run/file. Thus, no need to have basket.
        """
        f = self.file
        f['run'] = rq

    def write_event_rq(self, rq: EventRQBasket):
        """
        Write one basket at a time
        """
        f = self.file
        f['event'].extend({
            "event_id": rq.event_id,
            "n_pulses": rq.n_pulses,
            "pulse_id": ak.Array(rq.pulse_id),
            "pulse_start": ak.Array(rq.pulse_start),
            "pulse_end": ak.Array(rq.pulse_end),
            "pulse_area_adc": ak.Array(rq.pulse_area_adc),
            "pulse_height_adc": ak.Array(rq.pulse_height_adc),
            "pulse_coincidence": ak.Array(rq.pulse_coincidence),
        })

    def remove_branches(self):
        """
        writing awkward array is annoying, it create one extra
        branch for length. I do not like it since I have been tracking it
        This is not a crucial task though.
        """
        pass

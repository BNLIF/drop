'''
Outline
- baseline subtraction per channel
- pulse finding
- sum channels
'''
from numpy import zeros

from caen_reader import RawDataFile
from caen_reader import RawTrigger
from yaml_reader import CONFIG
from numpy.lib.stride_tricks import sliding_window_view

class Pulses:
    pulses_start = []
    pulses_end = []
    area = []

class Waveform(RawTrigger):

    def __init__(self, yaml_data):
        super(RawTrigger, self).__init__()
        self.roll_len = int(CONFIG['rolling_length'])
        self.sigma_thr = float(CONFIG['sigma_above_baseline'])
        self.daq_len = int(CONFIG['daq_length'])
        self.pre_pulse = int(CONFIG['pre_pulse'])
        self.post_pulse = int(CONFIG['post_pulse'])

    def baseline_finder(self):
        mean=zeros(self.daq_len)
        std =zeros(self.daq_len)
        for kw, val in self.traces.items():
            v = sliding_window_view(val, self.roll_len)
            roll_start = self.roll_len-1
            mean[roll_start:] = v.mean(axis=-1)
            std[roll_start:] = v.std(axis=-1)
            thre = mean-std*self.sigma_thr

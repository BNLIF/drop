import yaml
from numpy import array

"""
The following parameters do not change often. So hard coded here
"""
ADC_RATE_HZ=5e8 # Hz

class ScipyPeakFindingParam():
    """
    Collection of scipy peak finder parameters
    """
    distance = None
    thresold = None
    height = None


class YamlReader():
    def __init__(self, file_path=None):
        self.file_path=file_path
        with open(file_path, "r") as f:
            try:
                self.data = yaml.safe_load(f)
                self.type_casting()
            except yaml.YAMLError as exc:
                print(exc)

    def type_casting(self):
        """
        The right variable type
        """
        self.batch_size = int(self.data['batch_size'])
        self.post_trigger = int(self.data['post_trigger'])
        self.dgtz_dynamic_range_mV = int(self.data['dgtz_dynamic_range_mV'])
        self.apply_high_pass_filter = bool(self.data['apply_high_pass_filter'])
        self.high_pass_cutoff_Hz = float(self.data['high_pass_cutoff_Hz'])
        self.moving_avg_length = int(self.data['moving_avg_length'])
        self.sigma_above_baseline = float(self.data['sigma_above_baseline'])
        self.pre_pulse = int(self.data['pre_pulse'])
        self.post_pulse = int(self.data['post_pulse'])

        self.roi_start = array(self.data['roi_start'], dtype=int)
        self.roi_end = array(self.data['roi_end'], dtype=int)
        self.pre_roi_length = int(self.data['pre_roi_length'])

        self.pulse_finder_algo = int(self.data['pulse_finder_algo'])
        self.scipy_pf_pars = ScipyPeakFindingParam()
        self.scipy_pf_pars.distance = int(self.data['scipy_peak_finder_parameters']['distance'])
        self.scipy_pf_pars.threshold = int(self.data['scipy_peak_finder_parameters']['threshold'])
        self.scipy_pf_pars.height = int(self.data['scipy_peak_finder_parameters']['height'])

        return None

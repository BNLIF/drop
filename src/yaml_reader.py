import yaml
from numpy import array

"""
The following parameters do not change often. So hard coded here
"""
SAMPLE_TO_NS=2

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

    def get_ch_names(self, input_list):
        """
        Allow user to specify channels using different conventions.
        For example: 101 -> adc_b1_ch1, or b1_ch1 -> adc_b1_ch1
        """
        if isinstance(input_list, list):
            ch_names = []
            for item in input_list:
                if type(item)==str:
                    if item[0:4]=='adc_':
                        ch_names.append(item)
                    elif 'ch' in item:
                        ch_names.append('adc_'+item)
                    elif item.isdigit():
                        chid = int(item)%100
                        boardId = int(item) // 100
                        ch_str = 'adc_b%d_ch%d' % (boardId, chid)
                        ch_names.append(ch_str)
                    else:
                        print('ERROR: string type not recognized:', item)
                elif isinstance(item, int):
                    chid = item%100
                    boardId = item//100
                    ch_str = 'adc_b%d_ch%d' % (boardId, chid)
                    ch_names.append(ch_str)
                else:
                    print('ERROR: not recognized element in user_list')
            return ch_names
        else:
            print("ERROR: not a list")

    def type_casting(self):
        """
        The right variable type
        """
        self.batch_size = int(self.data['batch_size'])
        self.post_trigger = float(self.data['post_trigger'])
        self.dgtz_dynamic_range_mV = int(self.data['dgtz_dynamic_range_mV'])
        self.non_signal_channels= self.get_ch_names( self.data['non_signal_channels'] )
        self.bottom_pmt_channels= self.get_ch_names( self.data['bottom_pmt_channels'] )
        self.side_pmt_channels= self.get_ch_names( self.data['side_pmt_channels'] )
        self.spe_fit_results_path = self.data['spe_fit_results_path']

        self.daisy_chain = bool(self.data['daisy_chain'])
        self.apply_high_pass_filter = bool(self.data['apply_high_pass_filter'])
        self.high_pass_cutoff_Hz = float(self.data['high_pass_cutoff_Hz'])
        self.moving_avg_length = int(self.data['moving_avg_length'])
        self.sigma_above_baseline = float(self.data['sigma_above_baseline'])
        self.pre_pulse = int(self.data['pre_pulse'])
        self.post_pulse = int(self.data['post_pulse'])


        self.roi_start_ns = array(self.data['roi_start_ns'], dtype=int)
        self.roi_end_ns = array(self.data['roi_end_ns'], dtype=int)

        self.pulse_finder_algo = int(self.data['pulse_finder_algo'])
        self.scipy_pf_pars = ScipyPeakFindingParam()
        self.scipy_pf_pars.distance = int(self.data['scipy_peak_finder_parameters']['distance'])
        self.scipy_pf_pars.threshold = int(self.data['scipy_peak_finder_parameters']['threshold'])
        self.scipy_pf_pars.height = int(self.data['scipy_peak_finder_parameters']['height'])
        self.scipy_pf_pars.prominence = int(self.data['scipy_peak_finder_parameters']['prominence'])
        self.spe_height_threshold = float(self.data['spe_height_threshold'])

        return None

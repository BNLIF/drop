# Config Files

## DAQ Setting
- `batch_size`: int. batch_size specifies the number of events to process in one batch. Load and process one batch at a time. The bigger the batch, the more the memory needed.
- `post_trigger`: float. Fraction of acquisition after trigger.
- `daisy_chain`: bool. True if digitizer trigger are in daisy chain.
- `dgtz_dynamic_range_mV`: int. Two acceptable options for V1730s: 2000 or 500.
- `non_signal_channels`: list of str, or list of int. Non-signal channels are also called auxiliary channel in code. For example, muon paddles are not considered signal, but digitized to provide supplementary info. Need to know auxiliary channels to reconstruction them separately.
- `bottom_pmt_channels`: list of str, or list of int.. List of channels for bottom PMTs.
- `side_pmt_channels`: list of str, or list of int.. List of channels for side PMTs.

## Calibration info
- `spe_fit_results_file`: str. SPE calibration are saved to a csv file. By default YamlReader looks for this file in yaml directory (same directory as this config file). Example: `bnl1t_spe_fit_results_220826.csv`

## Event Reconstruction Config

### Noise Filter
- `apply_high_pass_filter`: bool. Apply high pass filter or not. Do not recommend.
- `high_pass_cutoff_Hz`: float, high pass filter threshold
- `rolling_length`: int. rolling baseline window. **THIS IS NOT USED FOR NOW**
- `sigma_above_baseline`: float. sigma above threshold in rolling baseline. **THIS IS NOT USED FOR NOW**
- `pre_pulse`: int. Number of samples after pulse peak. **THIS IS NOT USED FOR NOW**
- `post_pulse`: int. Number of samples before pulse peak. **THIS IS NOT USED FOR NOW**

### ROI Assocaited
- `roi_start`: list. ROI start time in ns. `roi_start` is defined with respect to the trigger arrival time of the master boards.
- `roi_end`: list. ROI end time in ns. `roi_end` is defined with respect to the trigger arrival time of the master boards.

> **Note**: The RQWriter will saves three ROI. For example, `roi_start_ns: [-200, -50, 200]` and `roi_end_ns: [-100, 50, 300]` define three 100ns ROIs. The first starts 200 ns before master trigger time. (MTT) The second start 50ns before and ends 50ns after MTT. The third starts 200 ns after MTT.

### scipy peak finding
- `pulse_finder_algo`: int. Options to chooose pulse finding algorthim. 0 is scipy peak finder
- `scipy_peak_finder_parameters`:
  - `distance`: float. Required minimal horizontal distance (>= 1) in samples between neighbouring peaks. Smaller peaks are removed first until the condition is fulfilled for all remaining peaks.
	- `threshold`: float. Required threshold of peaks, the vertical distance to its neighboring samples. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required threshold.
  	- `height` float. Required height of peaks. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required height.
    - `prominence`: float. The prominence of a peak may be defined as the least drop in height necessary in order to get from the summit to any higher terrain.
- `spe_height_threshold`: float. if a pulse-channel height is above this threshold, it's counted toward coincidence

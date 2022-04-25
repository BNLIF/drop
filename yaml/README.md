# Config Files

## DAQ Setting
- `batch_size`: int. batch_size specifies the number of events to process in one batch.
- `daq_length`: int. Number of acquisition samples specified in LabVIEW. Note: the actual useful length saved to file is less. 
- `post_trigger`: float. Fraction of acquisition after trigger.

## ROI Assocaited
- `roi_start`: list. Frist sample index of roi integral
- `roi_end`: list. Last sample index of roi integral
- `pre_roi_length`: int. Region before ROI, used for baseline subtraction.

## Waveform
- `apply_high_pass_filter`: bool. Apply high pass filter or not
- `high_pass_cutoff_Hz`: float, high pass filter threshold
- `rolling_length`: int. rolling baseline window
- `sigma_above_baseline`: float. sigma above threshold in rolling baseline
- `pre_pulse`: int. Number of samples after pulse peak
- `post_pulse`: int. Number of samples before pulse peak.

## scipy peak finding
- `scipy_find_peaks`:
	-`distance`: float. Required minimal horizontal distance (>= 1) in samples between neighbouring peaks. Smaller peaks are removed first until the condition is fulfilled for all remaining peaks.
	- `threshold`: float. Required threshold of peaks, the vertical distance to its neighboring samples. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required threshold.
  	- `height` float. Required height of peaks. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required height.

# Config Files

## DAQ Setting
- `n_boards`: int. Number of digitizer board taking data.
- `daq_length`: int. Number of samples in DAQ window. (Note: LabVIEW setting is not necessarily the same as recorded in file)
- `post_trigger`: float. 
- `boardId_order`: list. Order of board recorded in file. Usually master board is the first. (note: check_boardId_order.py)

## Input/Output
- data_dir: str
- output_dir: str

## ROI Assocaited
- roi_start: [290, 380]
- roi_end: [320, 450]
- pre_roi_length: 100

## Rolling Baseline
- rolling_length: 50
- sigma_above_baseline: 3.0
- pre_pulse: int
- post_pulse: int

## scipy peak finding
- scipy_find_peaks:
	-distance:
	- threshold: 
  	- height: 

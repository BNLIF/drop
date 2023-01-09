> This markdown document is manually maintained.

# RQ
A brief summary of Reduced Quality (RQ) variables in root file. The RQ files contain high level reconstructed event information from waveforms. RQ is a terminology from the LZ experiment, and other experiments call them ntuples or DSTs.

The RQs are stored in ROOT TTrees in a ROOT file, typically with the suffix `_rq` in its name.

## Data structure Overview

The data are saved in ROOT tree structure. A tree has many branches, but all branches have the same number of entries, or sometimes we say the same number of events. Imagine a tree as a giant table:
|         | branch 1 | branch 2 | branch 3 | ... |
|:-------:|:--------:|:--------:|:--------:|:---:|
| entry 0 |          |          |          |     |
| entry 1 |          |          |          |     |
| entry 2 |          |          |          |     |
|   ...   |          |          |          |     |

where each entry (or each event) is described by the features stored in many branches. When loading a tree branch in uproot, for example:
```python
f = uproot.open('path/to/your/rq/file')
t = f['event'] # event is a tree name
b1 = t['pulse_area_sum_pe'].array(library='np') # pulse_area_sum_pe is a branch name
```
you're loading the entire column named `pulse_area_sum_pe` of that giant table. So the length of `b1` is the number of entries of the table. Suppose you load another branch like:
```python
b2 = t['event_ttt'].array(library='np') # event_ttt is a branch name
```
This branch `b2` will have the same length as `b1` even through the elements of `b1` and `b2` do not necessarily have the same data type. In this particular example, `b2[0]` is an `uint32`, while `b1[0]` is a dynamic array.

## Tree: `run_info`

Run Info. Run-level info has exactly one entry per run.

| Tables		| type			 |		Description			|
|:------------ 	|----------------------| -------------------------------------------|
| start_year      	| uint16 		 | run start year		|
| start_month      	| uint16 		 | run start month		|
| start_day     	| uint16 		 | run start day				|
| start_hour      	| uint16 		 |run start hour				|
| start_minute      	| uint16 		 | run start minute			|
| n_boards      	| uint16 		 | number of digitizer boards			|
| n_event_proc      	| uint32		 | number of events processed			|
| n_trg_read 		| uint32      	  	 | number of triggers read from binary file	|
| leftover_event_id	| uint32 	 | the leftover event_id that are not saved to root file; some events/triggers may be droppd druing data readout |
| active_ch_id		|  uint16[n_ch]	 | unique id for all active channels      	       |

In addition, the yaml configuration file are also saved to run_info tree. They're labelled as `cfg_*`, The `cfg_*` names are self-explanatory. See [yaml/README.md] (https://github.com/BNLIF/drop/blob/main/yaml/README.md)).

> Note: uproot cannot save string. A string is broken into a list of ASCII char, and saved as list of int. After load in python, need to convert: [int] -> [char] -> str. For example, "cat" -> ['c', 'a', 't'] -> [99, 97, 116] -> saved. To recovery the str, use chr(int): [chr(i) for i in [99, 97, 116]] ->  ['c', 'a', 't'] -> "cat" .

## Tree: `pmt_info`

Calibrated PMT info. There are exactly `n_ch` entries. Variables are from the fit of led calibration. `spe` stands for single photoelectron.

| Tables		| type			 |		Description			|
|:------------ 	|----------------------| -------------------------------------------|
| ch_id      	| uint16 		 | number of digitizer boards			|
| spe_mean      	| float32		 | spe mean from fit. Unit: pC.			|
| spe_width      	| float32		 | spe width from fit. Unit: pC.			|
| spe_mean_err      	| float32		 | standard error for spe_mean. Unit: pC.			|
| spe_width_err      	| float32		 | standard error for spe_width. Unit: pC.			|
| chi2      	| float32		 | chi square			|
| dof		| uint16		 | number of degree of freedom			|
| HV		| int16		 | PMT bias voltage value. unit: volt 				| 	    

`spe_mean` is used to convert mV to PE/ns. It's possible to reverse engineering and calculate a channel variable in mV (or mV*ns) from a PE/ns (or PE) unit. For example, the digitizer has a 14-bit range for Vpp=2 dynamic range, so the conversion factor from ADC to mV is: `2000/(2^14-1)`. Since the digitizer has an input impedance of 50 Ohm, the conversion of mV to PE/ns is `1/50/spe_mean`

## Tree: `event`
Event info.

So what is an event?

The short version: an event is a muon (most of the time) passing through the top paddles and produce detectable lights in the liquid (water or WbLS).

The long version:
- **Triggering**. We have two scintillator paddles (dimension: 5 x 4 inch) on top of the tank. The two paddles are oriented 90 degree with each other. The two paddles are connected to discriminators (50 ns length), and whenever there is a coincidence between the two discriminators, we have a trigger signal. The three v1730s digitizers are in daisy chain. When a trigger signal is received by the first board (master), it’s propagated to the second board (slave 1), and subsequently propagated to the third board (slave 2). The default DAQ length for muon data is 4 us per board (500 ns before, and 3.5us after trigger). The trigger propagation within a board has a 48 ns delay, so the waveform recorded by three boards will have offset in time (DROP took care of them when calculating ntuple variables).
- **Data processing**. All three boards data are stored in the same binary file. During the conversion from raw binary to raw root format, board 1, 2, 3 are matched based on their event Id. An event in raw data are really just the adc traces from the 48 all channels (3 boards, 16ch each) — 46 channels are used for PMTs, and 2 are used for the bottom paddles. Then DROP converts the raw waveform into ntuple format, and that’s the variables you see in this document.

### Event level variables
One per event.

| Variable Name | type		| Description		|
|:------------ |-------------| -----------------	|
| event_id      | uint32	| unique event id	|	   
| event_ttt     | uint64	| trigger time tag (8 ns/counter)	|
| event_sanity  | uint32        | sanity of an event    |
| event_saturated  | bool        | True if any of the signal channels are saturated |
| npulse	     | uint32		| number of pulses				|

### Channel level variables

PMTs channel variables. Each branch is a static array of fixed size `n_ch`. ROI stands for region of interval, or region of interest. There are three ROIs per waveform. The ROI start and end time are defined in the yaml config file. ROI 0/1/2 suppose to contain intervals before/at/after trigger position. Quantities computed within the ROIs are area, height (peak height with respect to baseline), low (valley bottom with respect to baseline), std (standard deviation)

| Variable Name      | type			| Description						|
|:------------      |---------------		| ---------------------------------------		|
| ch_id		    | uint16[n_ch]		| id for PMT channel					|
| ch_saturated		 | bool[n_ch]		| true if this channel is saturated					|
| ch_roi0_height_pe | float32[n_ch]	| max height (peak) in pe/ns within roi 0 (see yaml file for interval definition)	|
| ch_roi1_height_pe | float32[n_ch]	| max height (peak) in pe/ns within roi 1 	|
| ch_roi2_height_pe | float32[n_ch]	| max height (peak) in pe/ns within roi 2	|
| ch_roi0_area_pe   | float32[n_ch]	| area in pe within roi 0 (see yaml file)		|
| ch_roi1_area_pe   | float32[n_ch] 	| area in pe within roi 1 (see yaml file)		|
| ch_roi2_area_pe   | float32[n_ch] 	| area in pe within roi 2 (see yaml file)		|
| ch_roi0_low_pe   | float32[n_ch]	| lowest height (valley) in pe/ns within roi 0		|
| ch_roi1_low_pe   | float32[n_ch] 	| lowest height (valley) in pe/ns within roi 1 		|
| ch_roi2_low_pe   | float32[n_ch] 	| lowest height (valley) in pe/ns within roi 2 		|
| ch_roi0_std_pe   | float32[n_ch]	| standard deviation in pe/ns within roi 0		|
| ch_roi1_std_pe   | float32[n_ch] 	| standard deviation in pe/ns within roi 1		|
| ch_roi2_std_pe   | float32[n_ch] 	| standard deviation in pe/ns within roi 2		|
| ch_roi0_std_mV   | float32[n_ch] 	| standard deviation in mV within roi 0. Remove SPE normalization helps gauge baseline noise.|

### Auxilary channel variables

Auxilary (non-signal) channels provide extra info. For example, paddle is considered aux channel. Each branch is a static array of size `n_aux_ch`.

| Variable Name      | type                     | Description                                           |
|:------------      |---------------            | ---------------------------------------               |
| aux_ch_id         | uint16[n_aux_ch]            | id for auxiliary channel                             |
| aux_ch_area_mV | float32[n_aux_ch] | channel area in mV      |


### Pulse level variables
Pulse level variables are dynamic arrays -- we only know array during the data processing. The length of array is specified by `npulse` variable, defined as an the event-level variable above. Pulses are order by [prominence](https://en.wikipedia.org/wiki/Topographic_prominence), and in decending order, so the first pulse is normally the largest one.

| Variable Name      | type		| Description					|
|:------------      |---------------	| -----------------				|
| pulse_id	     | uint32[npulse]	| unique pulse id.   	   			|
| pulse_start        | uint32[npulse]	| the start index of a pulse			|
| pulse_end	     | uint32[npulse]	| the end index of a pulse			|
| pulse_area_sum_pe     | float32[npulse]	| summed PMT area in pe. Area is integrated from `pulse_start` to `pulse_end`. 		|
| pulse_area_bot_pe     | float32[npulse]	| summed bottom PMT area in pe. Area is integrated from `pulse_start` to `pulse_end`.	|
| pulse_area_side_pe     | float32[npulse]	| summed side PMT area in pe. Area is integrated from  `pulse_start` to `pulse_end`.  |
| pulse_area_row1_pe    | float32[npulse]	| summed row 1 PMT area in pe.  Row 1 is the highest 4 side PMTs (ex. b1_p1, b2_p1, b3_p1, b4_p1). |
| pulse_area_row2_pe    | float32[npulse]	| summed row 2 PMT area in pe. Row 2 is the second highest 4 side PMTs (ex. b1_p2, b2_p2, b3_p2, b4_p2). |
| pulse_area_row3_pe    | float32[npulse]	| summed row 3 PMT area in pe. Row 3 is the third highest 4 side PMTs (ex. b1_p3, b2_p3, b3_p3, b4_p3). |
| pulse_area_row4_pe    | float32[npulse]	| summed row 4 PMT area in pe. Row 4 is the lowest 4 side PMTs (ex. b1_p4, b2_p4, b3_p4, b4_p4). |
| pulse_area_col1_pe    | float32[npulse]	| summed column 1 PMT area in pe.  Col 1 is the cloest 4 side PMTs to the darkroom door (ex. b1_p*). |
| pulse_area_col2_pe    | float32[npulse]	| summed column 2 PMT area in pe. Col 2 is the farest 4 side PMTs to the PC (ex. b2_p*). |
| pulse_area_col3_pe    | float32[npulse]	| summed column 3 PMT area in pe. Col 3 is the cloest 4 side PMTs to the PC (ex. b3_p*). |
| pulse_area_col4_pe    | float32[npulse]	| summed column 4 PMT area in pe. Col 4 is the farest 4 side PMTs to the darkroom door (ex. b4_p*). |
| pulse_area_user_pe    | float32[npulse]	| summed of a list of channels defined by user. See yaml/config.yaml file. |
| pulse_aft10_sum_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 10% of total pulse area. Unit: ns  |
| pulse_aft10_bot_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 10% of bottom PMT pulse area. Unit: ns  |
| pulse_aft10_side_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 10% of side PMT pulse area. Unit: ns  |
| pulse_aft10_row1_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 10% of row1 PMT pulse area. Unit: ns  |
| pulse_aft10_row2_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 10% of row2 PMT pulse area. Unit: ns  |
| pulse_aft10_row3_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 10% of row3 PMT pulse area. Unit: ns  |
| pulse_aft10_row4_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 10% of row4 PMT pulse area. Unit: ns  |
| pulse_aft90_sum_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 90% of total pulse area. Unit: ns  |
| pulse_aft90_bot_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 90% of bottom PMT pulse area. Unit: ns  |
| pulse_aft90_side_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 90% of side PMT pulse area. Unit: ns  |
| pulse_aft90_row1_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 90% of row1 PMT pulse area. Unit: ns  |
| pulse_aft90_row2_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 90% of row2 PMT pulse area. Unit: ns  |
| pulse_aft90_row3_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 90% of row3 PMT pulse area. Unit: ns  |
| pulse_aft90_row4_ns    | float32[npulse]	| Area Fraction Time (AFT) is the time reaching 90% of row4 PMT pulse area. Unit: ns  |
| pulse_rise_sum_ns    | float32[npulse]	| Simple rise-time (delta time from 10% to 90% pulse height), computed using all PMTs. No fit. Unit: ns  |
| pulse_rise_bot_ns    | float32[npulse]	| Simple rise-time (delta time from 10% to 90% pulse height), computed using bottom PMTs. No fit. Unit: ns  |
| pulse_rise_side_ns    | float32[npulse]	| Simple rise-time (delta time from 10% to 90% pulse height), computed using side PMTs. No fit. Unit: ns  |
| pulse_fall_sum_ns    | float32[npulse]	| Simple fall-time (delta time from 90% to 10% pulse height), computed using all PMTs. No fit. Unit: ns  |
| pulse_fall_bot_ns    | float32[npulse]	| Simple fall-time (delta time from 90% to 10% pulse height), computed using bottom PMTs. No fit. Unit: ns  |
| pulse_fall_side_ns    | float32[npulse]	| Simple fall-time (delta time from 90% to 10% pulse height), computed using side PMTs. No fit. Unit: ns  |
| pulse_fp40_sum         | float32[npulse]	| Pulse prompt fraction. The fraction of PE in the first 40ns in summed PMT. Unit: dimensionless  |
| pulse_fp40_bot         | float32[npulse]	| Pulse prompt fraction. The fraction of PE in the first 40ns in bottom PMT. Unit: dimensionless  |
| pulse_fp40_side         | float32[npulse]	| Pulse prompt fraction. The fraction of PE in the first 40ns in side PMT. Unit: dimensionless  |
| pulse_height_sum_pe     | float32[npulse]	| max height of this pulse in the sum channel, unit pe/ns 		|
| pulse_height_bot_pe     | float32[npulse]	| max height of this pulse in the sum of bottom PMTs, unit pe/ns	|
| pulse_height_side_pe     | float32[npulse]	| max height of this pulse in the summed side PMTs, unit pe/ns  |
| pulse_sba  | uint32[npulse]	| side-to-bottom asymmetry: (`pulse_area_side_pe`-`pulse_area_bot_pe`)/`pulse_area_sum_pe` |
| pulse_ptime_ns  | uint32[npulse]	| peak time in ns |
| pulse_coincidence  | uint32[npulse]	| number of PMTs passing thresholds within `pulse_start` to `pulse_end` |
| pulse_area_max_frac  | uint32[npulse]	| max channel fraction. Area in max channel / total area, for all channels|
| pulse_area_max_ch_id  | uint32[npulse]	| The id for the channel that has the max area frac.  |
| pulse_area_bot_max_frac  | uint32[npulse]	| max channel fraction in bottom PMTs. Area in max channel / total area, for all channels|
| pulse_area_bot_max_ch_id  | uint32[npulse]	| The id for the bottom channel that has the max area bot frac.  |
| pulse_saturated  | vector\<bool\>	| True if this pulse is saturated. |

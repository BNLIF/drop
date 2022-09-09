> This markdown document is manually created on Jun 2 2022. Feel free to update it.
> Last Update: Sept 8 2022 by Xin

# RQ
A brief summary of Reduced Quality (RQ) variables in root file. The RQ files contain high level reconstructed event infomation from waveforms. Other experiments call them ntuples or DSTs.

The RQs are stored in ROOT TTrees in a ROOT file, typically with the suffix `_rq` in its name.

## Data structure Overview

The data are saved in ROOT tree structure. A tree has many branches, but all branches have the same number of entries, or sometimes we say the same number of events. Imagine a tree as a gaint table:
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
you're loading the entire column named `pulse_area_sum_pe` of that gaint table. So the length of `b1` is the number of entries of the table. Suppose you load another branch like:
```python
b2 = t['event_ttt'].array(library='np') # event_ttt is a branch name
```
This branch `b2` will have the same length as `b1` even through the elements of `b1` and `b2` do not necessarily have the same data type. In this particular example, `b2[0]` is an `uint32`, while `b1[0]` is a dynamic array. 

## Tree: `run_info`

Run Info.

| Tables		| type			 |		Description			|
|:------------ 	|----------------------| -------------------------------------------|
| n_boards      	| uint64 		 | number of digitizer boards			|
| n_event_proc      	| uint64		 | number of events processed			|
| n_trg_read 		| uint64      	  	 | number of triggers read from binary file	|
| leftover_event_id	| uint64 	 | the leftover event_id that are not saved to root file; some events/triggers may be droppd druing data readout |
| active_ch_id		|  uint64[n_ch]	 | unique id for all active channels      	       |

In addition, the yaml configuration file are also saved to run_info tree. They're labelled as `cfg_*`, The `cfg_*` names are self-explanatory. See [yaml/README.md] (https://github.com/BNLIF/drop/blob/main/yaml/README.md)).

> Note: uproot cannot save string. A string is broken into a list of ASCII char, and saved as list of int. After load in python, need to convert: [int] -> [char] -> str. For example, "cat" -> ['c', 'a', 't'] -> [99, 97, 116] -> saved. To recovery the str, use chr(int): [chr(i) for i in [99, 97, 116]] ->  ['c', 'a', 't'] -> "cat" .

## Tree: `pmt_info`

Calibrated PMT info. Variables are from fit.

| Tables		| type			 |		Description			|
|:------------ 	|----------------------| -------------------------------------------|
| ch_id      	| uint16 		 | number of digitizer boards			|
| spe_mean      	| float32		 | spe mean from fit			|
| spe_width      	| float32		 | spe width from fit			|
| spe_mean_err      	| float32		 | standard error for spe_mean			|
| spe_width_err      	| float32		 | standard error for spe_width			|
| chi2      	| float32		 | chi square			|
| dof		| uint16		 | number of degree of freedom			|
| HV		| int16		 | HV value in voltage 				| 	    

## Tree: `event`
Event info

### Event level variables
One per event

| Variable Name | type		| Description		|
|:------------ |-------------| -----------------	|
| event_id      | uint32	| unique event id	|	   
| event_ttt     | uint64	| trigger time tag (8 ns/counter)	|
| event_sanity  | uint32        | sanity of an event    |

### Channel level variables

PMTs channel variables. Each branch is a static array of fixed size `n_ch`.

| Variable Name      | type			| Description						|
|:------------      |---------------		| ---------------------------------------		|
| ch_id		    | uint16[n_ch]		| id for PMT channel					|
| ch_roi0_height_pe | float32[n_ch]	| max height in pe/ns within roi 0 (see yaml file)	|
| ch_roi1_height_pe | float32[n_ch]	| max height in pe/ns within roi 1 (see yaml file)	|
| ch_roi2_height_pe | float32[n_ch]	| max height in pe/ns within roi 2 (see yaml file)	|
| ch_roi0_area_pe   | float32[n_ch]	| area in pe within roi 0 (see yaml file)		|
| ch_roi1_area_pe   | float32[n_ch] 	| area in pe within roi 1 (see yaml file)		|
| ch_roi2_area_pe   | float32[n_ch] 	| area in pe within roi 2 (see yaml file)		|

### Auxilary channel variables

Auxilary (non-signal) channels provide extra info. For example, paddle is considered aux channel. Each branch is a static array of size `n_aux_ch`.

| Variable Name      | type                     | Description                                           |
|:------------      |---------------            | ---------------------------------------               |
| aux_ch_id         | uint16[n_aux_ch]            | id for auxiliary channel                             |
| aux_ch_area_mV | float32[n_aux_ch] | channel area in mV      |


### Pulse level variables
Every event has `npulse` number of variables. Pulse branches are dynamic arrays. Pulses are order by [prominence](https://en.wikipedia.org/wiki/Topographic_prominence), and in decending order.

| Variable Name      | type		| Description					|
|:------------      |---------------	| -----------------				|
| npulse	     | uint32		| number of pulses				|
| pulse_id	     | vector\<uint32\>	| unique pulse id.   	   			|
| pulse_start        | vector\<uint32\>	| the start index of a pulse			|
| pulse_end	     | vector\<uint32\>	| the end index of a pulse			|
| pulse_area_sum_pe     | vector\<float32\>	| summed PMT area in pe from `pulse_start` to `pulse_end`. 		|
| pulse_area_bot_pe     | vector\<float32\>	| summed bottom PMT area in adc from `pulse_start` to `pulse_end`.	|
| pulse_area_side_pe     | vector\<float32\>	| summed side PMT area in adc from `pulse_start` to `pulse_end`.  |
| pulse_height_sum_pe     | vector\<float32\>	| max height of this pulse in the sum channel, unit pe/ns 		|
| pulse_height_bot_pe     | vector\<float32\>	| max height of this pulse in the sum of bottom PMTs, unit pe/ns	|
| pulse_height_side_pe     | vector\<float32\>	| max height of this pulse in the sum of side PMTs, unit pe/ns  |
| pulse_sba  | vector\<uint32\>	| side-to-bottom asymmetry: (`pulse_area_side_pe`-`pulse_area_bot_pe`)/`pulse_area_sum_pe` |
| pulse_ptime_ns  | vector\<uint32\>	| peak time in ns |
| pulse_coincidence  | vector\<uint32\>	| number of PMTs passing thresholds within `pulse_start` to `pulse_end` |
| pulse_area_max_frac  | vector\<uint32\>	| max channel fraction. Area in max channel / total area, for all channels|
| pulse_area_max_ch_id  | vector\<uint32\>	| max channel id. The  |

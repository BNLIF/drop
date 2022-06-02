
# RQ
A brief summary of Reduced Quality (RQ) variables in root file. The RQ files contain high level reconstructed event infomation from waveforms. A RQ root file is typically identified with `_rq` in its name.

> This markdown document is manually created on Jun 2 2022. Feel free to update it.

## Tree: `run_info`

Run Info.

| Tables		| type			 |		Description			|
|:------------ 	|----------------------| -------------------------------------------|
| n_boards      	| uint32 		 | number of digitizer boards			|
| n_event_proc      	| uint32		 | number of events processed			|
| n_trg_read 		| uint32      	  	 | number of triggers read from binary file	|
| leftover_event_id	| vector<uint32> 	 | the leftover event_id that are not saved to root file; some events/triggers may be droppd druing data readout |
| active_ch_id		|  vector<uint32>	 | unique id for active channels      	       |

## Tree: `event`
Event info

### Event level variables
One per event

| Variable Name | type		| Description		|
|:------------ |-------------| -----------------	|
| event_id      | uint32	| unique event id	|	   
| event_ttt     | uint32	| trigger time tag	|


### Pulse level variables
Every event has `npulse` number of variables

| Variable Name      | type		| Description					|
|:------------      |---------------	| -----------------				|
| npulse	     | uint32		| number of pulses				|
| pulse_id	     | vector<uint32>	| unique pulse id, sorted   	   		|
| pulse_start        | vector<uint32>	| the start index of a pulse			|
| pulse_end	     | vector<uint32>	| the end index of a pulse			|
| pulse_area_adc     | vector<float32>	| summed channel area in adc from `pulse_start` to `pulse_end`. To convert it to the unit of adc*ns, multiple by 2 since V1730 is 2 ns/sample. 		|
| pulse_height_adc   | vector<float32>	| max height in adc from `pulse_start` to `pulse_end` |
| pulse_coincidence  | vector<uint32>	| number of active channels passing thresholds within `pulse_start` to `pulse_end` |

### Channel level variables
Every event has `nch` number of variables

| Variable Name      | type		| Description						|
|:------------      |---------------	| ---------------------------------------		|
| nch	     	     | uint32		| number of active channels				|
| ch_roi0_height_adc | vector<float32>	| max height in adc within roi 0 (see yaml file)	|
| ch_roi1_height_adc | vector<float32>	| max height in adc within roi 1 (see yaml file)	|
| ch_roi0_area_adc   | vector<float32>	| area in adc within roi 0 (see yaml file)		|
| ch_roi1_area_adc   | vector<float32> 	| area in adc within roi 1 (see yaml file)		|
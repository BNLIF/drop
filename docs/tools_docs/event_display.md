<!-- markdownlint-disable -->

<a href="../../tools/event_display.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `event_display`
Simple Event Display 

PYTHONPATH is specified in setup.sh 

**Global Variables**
---------------
- **src_path**
- **YAML_DIR**
- **SAMPLE_TO_NS**


---

<a href="../../tools/event_display.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Args`








---

<a href="../../tools/event_display.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `EventDisplay`




<a href="../../tools/event_display.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `EventDisplay.__init__`

```python
__init__(raw_data_path, yaml_path=None)
```

Constructor: 

EventDisplay class to visualize individual waveform. This class recyles the same source code in drop/src. So details such as the baseline subtraction, SPE normalization, accumulated integral, and pulse finder results are consisent with DROP --- good for making cross-checks with the Reduced Quality (RQ) variables. 

Usage example:  event_display_example.ipynb. 



**Args:**
 
 - <b>`raw_data_path`</b> (str):  path to the raw root file 
 - <b>`yaml_path`</b> (str):  path to the configuration yaml file (default:  yaml/config.yaml) 



**Notes:**

> Since EventDisplay uses DROP source code, brand new update may break the main EventDispaly in the main branch. Try `event_display` branch which contains an older but a frozen version of DROP. 




---

<a href="../../tools/event_display.py#L150"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `EventDisplay.display_waveform`

```python
display_waveform(event_id, ch, baseline_subtracted=True, no_show=False)
```

Plot waveform, for individual channel, all channels, summed channel, or selected summed channels. 



**Args:**
 
 - <b>`event_id`</b> (int):  the event you want to see 
 - <b>`ch`</b> (str):  the channel(s) you want to see. If ch is str type,  for example, `b1_ch10`, plot that individual channel. if `ch=sum`,  plot the summed channel; if `ch=all` for plot all channels at once.  if ch is a list, plot that list. 
 - <b>`baseline_subtracted`</b> (bool):  plot baseline_subtracted waveform or not.  summed channel waveform is only available in baseline subtracted  form, while others have this options. 
 - <b>`no_show`</b> (bool):  draw option 

---

<a href="../../tools/event_display.py#L466"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `EventDisplay.get_bottom_pmt_hit_pattern`

```python
get_bottom_pmt_hit_pattern(event_id, start_ns=0, end_ns=100)
```

Get the bottom PMT hit patterns 



**Args:**
 
 - <b>`event_id`</b> (int):  the event you want 
 - <b>`start_ns`</b> (int):  the first ns to include 
 - <b>`end_ns`</b> (int):  The end ns. Open end conv, ex: [start_ns, end_ns). 



**Notes:**

> WORK IN PROGRESS. THIS FUNCTION HAS NOT BEEN TESTED. 

---

<a href="../../tools/event_display.py#L108"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `EventDisplay.grab_events`

```python
grab_events(wanted_event_id)
```

Grab raw data matching event_id. Process them using RunDrop. 



**Args:**
 
 - <b>`wanted_event_id`</b>:  int or list. ex. [1000, 1001, 3000, 30]. The grabbed events will be sorted in that order. 

Return: int, length of events grabbed 

---

<a href="../../tools/event_display.py#L423"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `EventDisplay.set_bottom_pmt_positions`

```python
set_bottom_pmt_positions()
```

Location of PMTs, which is hard coded for now 

TODO: use tools/ratdb_reader.py, which can readin ratdb/geo file, and extract position from them. 

---

<a href="../../tools/event_display.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `EventDisplay.set_user_summed_channel_list`

```python
set_user_summed_channel_list(user_list: list)
```

Set a user-defined list of channels to plot. 



**Args:**
 
 - <b>`user_list`</b> (list):  a list of str or a list of int 



**Examples:**
 For example, the following list is sum of all side channels user_list=[300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315] 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

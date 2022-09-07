<!-- markdownlint-disable -->

<a href="../../src/waveform.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `waveform`
One waveform per event. 

Outline 
- baseline subtraction per channel 
- pulse finding 
- sum channels 

**Global Variables**
---------------
- **SAMPLE_TO_NS**
- **EPS**


---

<a href="../../src/waveform.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Waveform`
Waveform class. One waveform per event. 

<a href="../../src/waveform.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.__init__`

```python
__init__(cfg: yaml_reader.YamlReader)
```

Constructor. 



**Args:**
 
 - <b>`cfg`</b> (YamlReader):  the config objection from YamlReader class. 




---

<a href="../../src/waveform.py#L264"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.calc_aux_ch_info`

```python
calc_aux_ch_info()
```

Reconstruct simple variables for non-signal channels (auxiliary channel) For example, the paddles are non-signal channels that provides auxiliary info 

---

<a href="../../src/waveform.py#L141"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.correct_daisy_chain_trg_delay`

```python
correct_daisy_chain_trg_delay()
```

Shift a channel's waveform based on which board it is. The 48 ns delay from V1730s trg_in to trg_out is calibrated with a square pulse. We do not expect it changes. Hence hard coded below. 

Remember to shift trigger position too. 



**TODO:**
  1. save the delay in config yaml file.  2. what about FAN-OUT? 



**Notes:**

> boardId is baked into ch_name. 

---

<a href="../../src/waveform.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.define_trigger_position`

```python
define_trigger_position()
```

You have to define an event's trigger time. For simplicity, use time of the first trigger arrived at the master board. This is calculate based on DAQ length and post_trigger fraction. 

---

<a href="../../src/waveform.py#L124"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.do_spe_normalization`

```python
do_spe_normalization()
```

Do SPE normalization for all signal channels Muon paddle is considered non-signal channel, and hence not SPE normalized 

---

<a href="../../src/waveform.py#L207"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.find_ma_baseline`

```python
find_ma_baseline()
```





---

<a href="../../src/waveform.py#L219"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.find_roi_area`

```python
find_roi_area()
```

Calc Integral in the Region of Interest (ROI) whose start_ns and end_ns are defined in yaml config file. 



**Notes:**

> roi_start_ns and roi_end_ns are defined with respect to trigger time 

---

<a href="../../src/waveform.py#L241"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.find_roi_height`

```python
find_roi_height()
```

calc the height within the Region of Interest (ROI) whose start_ns and end_ns are defined in yaml config file 



**Notes:**

> roi_start_ns and roi_end_ns are defined with respect to trigger time 

---

<a href="../../src/waveform.py#L89"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.get_flat_baseline`

```python
get_flat_baseline(val)
```

Define a flat baseline. Find the median and std, and return them 



**Args:**
 
 - <b>`val`</b>:  array of float 

Return: float, float 

---

<a href="../../src/waveform.py#L199"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.integrate_waveform`

```python
integrate_waveform()
```

Compute accumulated integral of the waveform. Do not forget to multiple by the sample size (2ns for V1730s) as it's integral not accumulated sum. 

---

<a href="../../src/waveform.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.reset`

```python
reset()
```

Variables that needs to be reset from event to event 

---

<a href="../../src/waveform.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.set_raw_data`

```python
set_raw_data(val)
```

Set raw data. 

---

<a href="../../src/waveform.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.subtract_flat_baseline`

```python
subtract_flat_baseline()
```

Very basic: subratct a flat baseline for all channels. New variables are saved in class for later usage: flat_base_mV, flat_base_std_mV, amp_mV. 

---

<a href="../../src/waveform.py#L173"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.sum_channels`

```python
sum_channels()
```

Sum up channels. 
    - "sum" means the sum of all PMTs 
    - "bot" means the sum of all bottom PMTs 
    - "side" means the sum of all side PMTs 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

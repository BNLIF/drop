<!-- markdownlint-disable -->

<a href="../../src/pulse_finder.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pulse_finder`




**Global Variables**
---------------
- **SAMPLE_TO_NS**


---

<a href="../../src/pulse_finder.py#L8"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PulseFinder`
Finding pulses. 

<a href="../../src/pulse_finder.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.__init__`

```python
__init__(cfg: yaml_reader.YamlReader, wfm: waveform.Waveform)
```

Constructor 

Pulse finder identify pulses in the sum channels. A pulse is defined by pulse_start and pulse_end sample index, and labelled by pulse_id. Once a pulse is found (or defined), pulse variables are then calculated. If scipy pulse finder is used, pulses are order in decending order of prominence. 



**Args:**
 
 - <b>`cfg`</b> (YamlReader):  configuration by YamlReader class 
 - <b>`wfm`</b> (Waveform):  waveform by Waveform class 




---

<a href="../../src/pulse_finder.py#L123"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.calc_pulse_ch_info`

```python
calc_pulse_ch_info()
```

Calculate pulse x channel variables. One per pulse per channel, excluding padles and summed channels. 

TODO: these variables are calcualted but not yet saved. 

---

<a href="../../src/pulse_finder.py#L148"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.calc_pulse_info`

```python
calc_pulse_info()
```

Calculate pulse-level variables. One event may have many pulses. 

area: integral in unit of PE height: max height in unit of PE/ns ptime_ns: peak time in ns sba: side bottom asymmetry coincidence: number of PMTs whose pulse height pass threshold area_max_frac: fraction of light in max PMTs ... [add more if you wish] 

---

<a href="../../src/pulse_finder.py#L208"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.display`

```python
display(ch='sum')
```

A plotting function showcase pulse finder. 



**Args:**
 
 - <b>`ch`</b> (str, list):   specified a channel to dispaly. 
 - <b>`ex. b1_ch0, ['b1_ch0', 'b1_ch1']. Default`</b>:  sum 



**Notes:**

> depricated? At least X.X. does not recall using it recently. 

---

<a href="../../src/pulse_finder.py#L83"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.find_pulses`

```python
find_pulses()
```

As the name suggests, find pulses. A pulse is defined from a start sample to an end sample. Assign unique pulse id starting from 0. 

This function assume pulse is postively polarized, only run this after baseline subtraction, and flip polarity. See Waveform::subtract_flat_baseline. 

---

<a href="../../src/pulse_finder.py#L204"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.is_spe`

```python
is_spe(ch='sum') → bool
```

Work in Progress  

---

<a href="../../src/pulse_finder.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.reset`

```python
reset()
```

Variables that needs to be reset per event 



**Notes:**

> If you want to add more pulse variables, do not forget to reset it here. 

---

<a href="../../src/pulse_finder.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.scipy_find_peaks`

```python
scipy_find_peaks()
```

Scipy find_peaks functions. The parameters can be tuned in the yaml file. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

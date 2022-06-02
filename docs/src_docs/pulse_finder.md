<!-- markdownlint-disable -->

<a href="../../src/pulse_finder.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pulse_finder`






---

<a href="../../src/pulse_finder.py#L7"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PulseFinder`
Finding pulses. 

<a href="../../src/pulse_finder.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.__init__`

```python
__init__(config: dict, wfm: waveform.Waveform)
```

Constructor 



**Args:**
 
 - <b>`config`</b> (dict):  yaml file config in dictionary 
 - <b>`wfm`</b> (Waveform):  waveform by Waveform class 



**Notes:**

> Initializes variables. When no pulse found, initial value are used. So better to have consistent initial type. 




---

<a href="../../src/pulse_finder.py#L104"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.display`

```python
display(ch='sum')
```

A plotting function showcase pulse finder 



**Args:**
 
 - <b>`ch`</b> (str, list):   specified a channel to dispaly. 
 - <b>`ex. b1_ch0, ['b1_ch0', 'b1_ch1']. Default`</b>:  sum 

---

<a href="../../src/pulse_finder.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.find_pulses`

```python
find_pulses()
```

Main function of PulseFinder. As the name suggests, find pulses. Only run this after baseline subtraction. 

---

<a href="../../src/pulse_finder.py#L100"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.is_spe`

```python
is_spe(ch='sum') → bool
```

Work in Progress  

---

<a href="../../src/pulse_finder.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.reset`

```python
reset()
```

Variables that needs to be reset per event 

---

<a href="../../src/pulse_finder.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PulseFinder.scipy_find_peaks`

```python
scipy_find_peaks()
```

Scipy find_peaks functions 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

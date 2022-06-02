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
- **ADC_RATE_HZ**
- **EPS**


---

<a href="../../src/waveform.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Waveform`
Waveform class. One waveform per event. 

<a href="../../src/waveform.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.__init__`

```python
__init__(config: dict)
```








---

<a href="../../src/waveform.py#L89"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.do_baseline_subtraction`

```python
do_baseline_subtraction()
```

Very basic Baseline is avg over all excluding trigger regions 

---

<a href="../../src/waveform.py#L143"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.do_rolling_baseline_subtraction`

```python
do_rolling_baseline_subtraction()
```

work in progress 

---

<a href="../../src/waveform.py#L147"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.find_roi_area`

```python
find_roi_area()
```





---

<a href="../../src/waveform.py#L164"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.find_roi_height`

```python
find_roi_height()
```





---

<a href="../../src/waveform.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.get_flat_baseline`

```python
get_flat_baseline(val)
```

define a flat baseline away from trigger Input: 
    - val: array 

---

<a href="../../src/waveform.py#L122"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.integrate_waveform`

```python
integrate_waveform()
```

integrated waveform 

---

<a href="../../src/waveform.py#L45"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.reset`

```python
reset()
```

Variables that needs to be reset from event to event 

---

<a href="../../src/waveform.py#L129"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.rolling_baseline`

```python
rolling_baseline()
```

work in progress 

---

<a href="../../src/waveform.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.set_ch_id`

```python
set_ch_id(val)
```





---

<a href="../../src/waveform.py#L59"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.set_ch_names`

```python
set_ch_names(val)
```





---

<a href="../../src/waveform.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.set_n_boards`

```python
set_n_boards(val)
```





---

<a href="../../src/waveform.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.set_raw_data`

```python
set_raw_data(val)
```





---

<a href="../../src/waveform.py#L108"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.sum_channels`

```python
sum_channels()
```

Sum all channels 

---

<a href="../../src/waveform.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Waveform.trigger_position`

```python
trigger_position()
```

finding trigger position (t0) 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

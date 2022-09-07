<!-- markdownlint-disable -->

<a href="../../src/rq_writer.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `rq_writer`






---

<a href="../../src/rq_writer.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RQWriter`
Write to file 

<a href="../../src/rq_writer.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RQWriter.__init__`

```python
__init__(args, n_pmt_ch, n_aux_ch, basket_size=1000)
```

Constructor: create root tree structure, fill, and write. The n_ch and n_aux_ch variables are needed to define branch structure (static array). Pulse-level variables are dynamic arrays, hence no need to define array size. Dynamic array is slower than static array. 



**Args:**
 
 - <b>`args`</b>:  input arguments passed to main, it includes output Directory 
 - <b>`n_ch`</b>:  number of channels used for PMTs (n_active_ch - n_aux_ch) 
 - <b>`n_aux_ch`</b>:  number of auxiliary (not-signal) channels 
 - <b>`batch_size`</b>:  number of entries per batch 




---

<a href="../../src/rq_writer.py#L242"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RQWriter.close`

```python
close()
```

remember to close file after done 

---

<a href="../../src/rq_writer.py#L86"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RQWriter.create_output`

```python
create_output()
```

First create output file name based on input file names Then create empty tree via mktree 

---

<a href="../../src/rq_writer.py#L286"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RQWriter.dump_event_rq`

```python
dump_event_rq()
```

Write one basket at a time 

---

<a href="../../src/rq_writer.py#L256"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RQWriter.dump_pmt_info`

```python
dump_pmt_info(df: pandas.core.frame.DataFrame)
```

uproot only accept dictionary 

---

<a href="../../src/rq_writer.py#L248"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RQWriter.dump_run_rq`

```python
dump_run_rq(rq: dict)
```

Write one per run/file. No need to loop. 

---

<a href="../../src/rq_writer.py#L149"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RQWriter.fill`

```python
fill(wfm: waveform.Waveform, pf: pulse_finder.PulseFinder)
```

Add variables to the basket. Append one event at a time. 



**Args:**
 
 - <b>`wfm`</b> (Waveform):  waveform from Waveform class. 
 - <b>`pf`</b> (PulseFinder):  from PulseFinder class 



**Notes:**

> The small but growing list of data types can be written as TTrees: * dict of NumPy arrays * Single numpy array * Awkward Array containing one level of variable length * a single Pandas DataFrame 
>So a list of numpy array is not an acceptable format. A list of list, on the other hand, is okay because it can be casted into a awkward array at extend stage. Hence, call tolist() below. I hope there is a better solution. https://uproot.readthedocs.io/en/latest/basic.html 

---

<a href="../../src/rq_writer.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RQWriter.reset`

```python
reset()
```

Variables that needs to be reset per batch of events 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

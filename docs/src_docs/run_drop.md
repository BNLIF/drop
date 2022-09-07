<!-- markdownlint-disable -->

<a href="../../src/run_drop.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `run_drop`
DROP convert raw waveform to reduced qualities. 

Contact: X. Xiang <xxiang@bnl.gov> 

**Global Variables**
---------------
- **MAX_N_EVENT**
- **YAML_DIR**

---

<a href="../../src/run_drop.py#L187"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main(argv)
```

Main function 


---

<a href="../../src/run_drop.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RunDROP`
Main Class. Once per run. Manage all operations. 

<a href="../../src/run_drop.py#L29"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RunDROP.__init__`

```python
__init__(args)
```



**Args:**
 
 - <b>`args`</b>:  return of parser.parse_args(). This is the input arguments  when you run the program 




---

<a href="../../src/run_drop.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RunDROP.load_pmt_info`

```python
load_pmt_info()
```

PMT calibration results are saved in a csv file The path to the csv file is specified in yaml config file 

---

<a href="../../src/run_drop.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RunDROP.load_run_info`

```python
load_run_info()
```

Load run_info tree, which contains only one entry. 



**Notes:**

> Not yet possible to save str via uproot. Use numbering convension: 100*boardId + chID. For example, 211 means board 2, channel 11, or `adc_b2_ch11`. 

---

<a href="../../src/run_drop.py#L107"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RunDROP.process_batch`

```python
process_batch(batch, writer: rq_writer.RQWriter)
```

Process one batch at a time. Batch size is defined in the yaml file. 



**Args:**
 
- batch (high-level awkward array): a collection of raw events 
- writer (RQWriter). If None, nothing to fill & write, but save to memory. 

---

<a href="../../src/run_drop.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RunDROP.sanity_check`

```python
sanity_check()
```

Collection of check before running 

---

<a href="../../src/run_drop.py#L175"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RunDROP.show_progress`

```python
show_progress()
```

print progress on screen 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

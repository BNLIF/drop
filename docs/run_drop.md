<!-- markdownlint-disable -->

<a href="../src/run_drop.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `run_drop`




**Global Variables**
---------------
- **MAX_N_EVENT**

---

<a href="../src/run_drop.py#L133"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main(argv)
```






---

<a href="../src/run_drop.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RunStatus`
An enumeration. 





---

<a href="../src/run_drop.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RunDROP`
Main Class. Once per run. Manage all operations. 

<a href="../src/run_drop.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RunDROP.__init__`

```python
__init__(args)
```

Constructor 



**Args:**
 
 - <b>`args`</b>:  return of parser.parse_args(). This is the input arguments  when you run the program 




---

<a href="../src/run_drop.py#L129"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RunDROP.display_ch_hits`

```python
display_ch_hits()
```

here or a separate toolbox class???  

---

<a href="../src/run_drop.py#L125"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RunDROP.display_wfm`

```python
display_wfm(ch=None)
```

display waveform 

---

<a href="../src/run_drop.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RunDROP.next`

```python
next()
```

Iterates to the next event. One Waveform per events. Each call iterates by one event, but one event may contain multiple triggers. getNextTrigger() iterates one trigger at a time. Carefully Check the boardId order. 



**Returns:**
 
 - <b>`RunStatus`</b>:  NORMAL (0), SKIP (1), STOP (2) 

---

<a href="../src/run_drop.py#L45"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RunDROP.sanity_check`

```python
sanity_check()
```

Collection of check before running 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

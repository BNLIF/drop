<!-- markdownlint-disable -->

<a href="../../src/raw_data_rooter.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `raw_data_rooter`
X. Xiang <xxiang@bnl.gov> 

Convert raw data from binary to root format for long term storage. No fancy event reconstruction. 

A trigger is a digitizer's data. Map triggers to events by using a event queue. An event queue is like a table: row->event_id, col->info 

Algotrhim in a nutshell: 0. Create an event queue 1. Read a trigger 2. Check this trigger's event_id in event queue; if not exist, create a new row in the queue. If exist, add to the row. 3. Periodically check if queue has any rows fully filled. If yes, dump the fully filled rows to file. 

**Global Variables**
---------------
- **N_BOARDS**
- **MAX_N_TRIGGERS**
- **DUMP_SIZE**
- **INITIAL_BASEKTEL_CAPACITY**
- **MAX_EVENT_QUEUE**

---

<a href="../../src/raw_data_rooter.py#L294"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main(argv)
```

Main function. Usage: python raw_data_rooter.py --help 


---

<a href="../../src/raw_data_rooter.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RunStatus`
An enumeration. 





---

<a href="../../src/raw_data_rooter.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RawDataRooter`
Convert BNL raw data collected by V1730 from binary to root 

<a href="../../src/raw_data_rooter.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.__init__`

```python
__init__(args)
```

Constructor 




---

<a href="../../src/raw_data_rooter.py#L272"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.close_file`

```python
close_file()
```

Close the open data file. Helpful when doing on-the-fly testing 

---

<a href="../../src/raw_data_rooter.py#L145"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.create_output_file`

```python
create_output_file()
```

Create output file 

---

<a href="../../src/raw_data_rooter.py#L215"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.dump_events`

```python
dump_events()
```

Dump fully filled events from queue to tree 

---

<a href="../../src/raw_data_rooter.py#L246"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.dump_run_info`

```python
dump_run_info()
```

Run tree contains meta data describing the DAQ config. One entry per run. 

---

<a href="../../src/raw_data_rooter.py#L181"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.fill_event_queue`

```python
fill_event_queue(trg)
```

Fill event queue, one trigger at a time. 

---

<a href="../../src/raw_data_rooter.py#L97"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.find_active_ch_names`

```python
find_active_ch_names()
```

Find active ch names by reading a few. 

---

<a href="../../src/raw_data_rooter.py#L203"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.get_full_queue_id`

```python
get_full_queue_id()
```

Return a set of event_id in queue that have all info filled 

---

<a href="../../src/raw_data_rooter.py#L115"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.next`

```python
next()
```

Iterate one trigger at a time. Careful check condition. If all good, fill event_queue. 



**Returns:**
 
 - <b>`RunStatus`</b>:  NORMAL, SKIP, STOP 

---

<a href="../../src/raw_data_rooter.py#L279"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.print_summary`

```python
print_summary()
```





---

<a href="../../src/raw_data_rooter.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.reset_event_queue`

```python
reset_event_queue()
```

Reset the event queue. 

---

<a href="../../src/raw_data_rooter.py#L80"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.sanity_check`

```python
sanity_check()
```

Werid thing may happen. Check.: 

---

<a href="../../src/raw_data_rooter.py#L288"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.show_progress`

```python
show_progress()
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

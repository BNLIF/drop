<!-- markdownlint-disable -->

<a href="../../src/raw_data_rooter.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `raw_data_rooter`
X. Xiang <xxiang@bnl.gov> 

Convert raw data from binary to root format for long term storage. No fancy event reconstruction. 

A trigger is a digitizer's data. Map triggers to events by using a event queue. An event queue is like a table: row->event_id, col->info 

Algotrhim in a nutshell:  0. Create an event queue  1. Read a trigger  2. Check this trigger's event_id in event queue; if not exist, create a new row in the queue. If exist, add to the row.  3. Periodically check if queue has any rows fully filled. If yes, dump the fully filled rows to file. 



**Notes:**

> The glogal parameters are all captialized. Make sure they are what you want. 

**Global Variables**
---------------
- **N_BOARDS**
- **DAQ_SOFTWARE**
- **MAX_N_TRIGGERS**
- **DUMP_SIZE**
- **INITIAL_BASKET_CAPACITY**
- **MAX_EVENT_QUEUE**
- **EXPECTED_FIRST_4_BYTES**

---

<a href="../../src/raw_data_rooter.py#L361"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main(argv)
```

Main function. Usage: python raw_data_rooter.py --help 


---

<a href="../../src/raw_data_rooter.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RunStatus`
An enumeration. 





---

<a href="../../src/raw_data_rooter.py#L56"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RawDataRooter`
Convert BNL raw data collected by V1730 from binary to root 

<a href="../../src/raw_data_rooter.py#L60"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.__init__`

```python
__init__(args)
```

Constructor 

RawDataRooter. 

args: the input arguments 




---

<a href="../../src/raw_data_rooter.py#L339"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.close_file`

```python
close_file()
```

Close the open data file. Helpful when doing on-the-fly testing 

---

<a href="../../src/raw_data_rooter.py#L188"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.create_output_file`

```python
create_output_file()
```

Create output file 

---

<a href="../../src/raw_data_rooter.py#L272"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.dump_events`

```python
dump_events()
```

Dump fully filled events from queue to tree 

---

<a href="../../src/raw_data_rooter.py#L310"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.dump_run_info`

```python
dump_run_info()
```

Run tree contains meta data describing the DAQ config. One entry per run. 

---

<a href="../../src/raw_data_rooter.py#L223"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.fill_event_queue`

```python
fill_event_queue(trg)
```

Fill event queue, one trigger at a time. Add TTT to the queue as well. If N_BOARDS>1, use board 1 as event ttt. event_sanity is added to flag bad events saved to binary file. event_sanity = 10^(boardId-1) + trigger_sanity. 



**Examples:**
  event_sanity = 0 means all good.  event_sanity = 100 means boardId=3 has sanity=1. other boards are 0. 



**Args:**
 
 - <b>`trg`</b> (RawTrigger):  RawTrigger class object from caen_reader module 

---

<a href="../../src/raw_data_rooter.py#L259"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.get_full_queue_id`

```python
get_full_queue_id()
```

Return a set of event_id in queue that have all info filled 

---

<a href="../../src/raw_data_rooter.py#L157"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.next`

```python
next()
```

Iterate one trigger at a time. Careful check condition. If all good, fill event_queue. 



**Returns:**
 
 - <b>`RunStatus`</b>:  NORMAL, SKIP, STOP 

---

<a href="../../src/raw_data_rooter.py#L115"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.preview_file`

```python
preview_file()
```

Preview the binary file to get necessary info to setup the processing: 
    - Find active ch names by reading a few. 
    - Find active boardId. 
    - Find number of samples. 



**Notes:**

> By default, it loads 100 triggers to get the info above. Error if bad. Smaller than 100 triggers? You may want to change the code. It's rare but not impossible to process a small file. 

---

<a href="../../src/raw_data_rooter.py#L346"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.print_summary`

```python
print_summary()
```





---

<a href="../../src/raw_data_rooter.py#L216"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.reset_event_queue`

```python
reset_event_queue()
```

Reset the event queue. 

---

<a href="../../src/raw_data_rooter.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.sanity_check`

```python
sanity_check()
```

Werid thing may happen. Check: 

---

<a href="../../src/raw_data_rooter.py#L355"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataRooter.show_progress`

```python
show_progress()
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

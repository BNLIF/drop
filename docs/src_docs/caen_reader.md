<!-- markdownlint-disable -->

<a href="../../src/caen_reader.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `caen_reader`




**Global Variables**
---------------
- **nan**


---

<a href="../../src/caen_reader.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RawDataFile`




<a href="../../src/caen_reader.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataFile.__init__`

```python
__init__(fileName, DAQ='WaveDump')
```

Initializes the dataFile instance to include the fileName, access time, and the number of boards in the file. Also opens the file for reading. 




---

<a href="../../src/caen_reader.py#L154"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataFile.close`

```python
close()
```

Close the open data file. Helpful when doing on-the-fly testing 

---

<a href="../../src/caen_reader.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawDataFile.getNextTrigger`

```python
getNextTrigger()
```

This function returns  the next trigger from the dataFile. It reads the control words into h[0-3], unpacks them, and then reads the next event. It returns a RawTrigger object, which includes the fileName, location in the file, and a dictionary of the traces :raise:IOError if the header does not pass a sanity check: (sanity = 1 if (i0 & 0xa0000000 == 0xa0000000) else 0 


---

<a href="../../src/caen_reader.py#L166"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RawTrigger`




<a href="../../src/caen_reader.py#L167"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawTrigger.__init__`

```python
__init__()
```

This is a class to contain a raw trigger from the .dat file. This is before any processing is done. It will contain a dictionary of the raw traces, as well as the fileName of the .dat file and the location of this trigger in the raw data. 




---

<a href="../../src/caen_reader.py#L183"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RawTrigger.display`

```python
display(trName=None)
```

A method to display any or all the traces in the RawTrigger object :param trName: string or list, name of trace to be displayed 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

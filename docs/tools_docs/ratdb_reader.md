<!-- markdownlint-disable -->

<a href="../../tools/ratdb_reader.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `ratdb_reader`
Description: Read a .RatDB file; it also read .geo file 

The loaded info are saved in self.tables 


---

<a href="../../tools/ratdb_reader.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `test`

```python
test()
```

Example how to use RatDBReader.  


---

<a href="../../tools/ratdb_reader.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RatDBReader`




<a href="../../tools/ratdb_reader.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RatDBReader.__init__`

```python
__init__(file_path=None)
```

Constructor. RatDB (geo) file reader. 



**Args:**
 
 - <b>`file_path`</b>:  str. path to your file.ratdb. 




---

<a href="../../tools/ratdb_reader.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `RatDBReader.load`

```python
load(file_path)
```

This function load ratdb file, and save them as a table. This function is called automatically in the constructor. You can call it again to update the table if file content has changed. 



**Args:**
 
 - <b>`file_path`</b>:  str 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

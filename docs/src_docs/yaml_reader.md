<!-- markdownlint-disable -->

<a href="../../src/yaml_reader.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `yaml_reader`




**Global Variables**
---------------
- **SAMPLE_TO_NS**


---

<a href="../../src/yaml_reader.py#L9"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ScipyPeakFindingParam`
Collection of scipy peak finder parameters 





---

<a href="../../src/yaml_reader.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `YamlReader`




<a href="../../src/yaml_reader.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `YamlReader.__init__`

```python
__init__(file_path=None)
```

Constructor 



**Args:**
  file_path (str). Path to yaml file. 




---

<a href="../../src/yaml_reader.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `YamlReader.get_ch_names`

```python
get_ch_names(input_list)
```

Allow user to specify channels using different conventions. For example: 101 -> adc_b1_ch1, or b1_ch1 -> adc_b1_ch1 



**Args:**
 
 - <b>`input_list`</b> (list):  list of str or list of int. 

---

<a href="../../src/yaml_reader.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `YamlReader.type_casting`

```python
type_casting()
```

The right variable type 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

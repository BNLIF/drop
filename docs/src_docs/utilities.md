<!-- markdownlint-disable -->

<a href="../../src/utilities.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `utilities`
Utility functions that are used by DROP 

**Global Variables**
---------------
- **SAMPLE_TO_NS**

---

<a href="../../src/utilities.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_colormap`

```python
generate_colormap(n_colors=32)
```

This function is copied from: https://stackoverflow.com/questions/42697933/colormap-with-maximum-distinguishable-colours For best visibility, set n_colors = number of channels 


---

<a href="../../src/utilities.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `digitial_butter_highpass_filter`

```python
digitial_butter_highpass_filter(data, cutoff_Hz=3000000.0)
```

data: 1d ndarray cutoff_Hz: cut off digitizer sampling freq in hz Source: https://scipy-cookbook.readthedocs.io/items/ButterworthBandpass.html 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._

Useful tools for debugging, and assisting high-level analysis.

# Event Display
See `event_display_example.ipynb` for the usage. You will need to download the data and run locally though.

# Print Binary Info 
Sometimes we want to inspect the raw binary from DAQ software. 

Usage. After setting enviromental variables, do:
```bash
python print_binary_info.py /path/to/raw_binary_file
```

# RatDB file reader
A python script that reads .ratdb (.geo) file as dictionary.

Usage. In python kernel, do
```python
from ratdb_reader import RatDBReader

r = RatDBReader(file_path=/path/to/your/file.ratdb)
```
That's it. The data are saved in `r.tables`. See `test()` example how to access it.

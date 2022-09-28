Useful tools for debugging, and assisting high-level analysis.

# Event Display
EventDisplay class allows plotting waveform easily. It uses the same underlying algorthim as DROP, so what you see via EventDisplay, is what you get in RQ/ntuple. See `event_display_example.ipynb` for the usage. You will need to download the data and run locally though.

# DQOM (Data Quality Offline Monitor)
It's important to get timely feedback on the data quality. Live monitor may be a long way to go, this offline monitor is a temp solution.

Usage. Enter the environment: `source env/bin/activate`, then do:
python dqom.py path/to/your/data

Alternative, use the bash script to run many at once:
```bash
. run_dqom.py file_list.txt
```
where file_list.txt is just file containing the path to data. For example, `file_list.txt` may look like this:

```
/media/disk_a/CERNBOX/WbLS-DATA/rq/v1.0.1/muon/phase1_muon_wbls_1pct_220921T1351_rq.root
/media/disk_a/CERNBOX/WbLS-DATA/rq/v1.0.1/muon/phase1_muon_wbls_1pct_220921T1609_rq.root
/media/disk_a/CERNBOX/WbLS-DATA/rq/v1.0.1/muon/phase1_muon_wbls_1pct_220921T2022_rq.root
/media/disk_a/CERNBOX/WbLS-DATA/rq/v1.0.1/muon/phase1_muon_wbls_1pct_220924T0748_rq.root
/media/disk_a/CERNBOX/WbLS-DATA/rq/v1.0.1/muon/phase1_muon_wbls_1pct_220923T0754_rq.root
/media/disk_a/CERNBOX/WbLS-DATA/rq/v1.0.1/muon/phase1_muon_wbls_1pct_220922T0007_rq.root
/media/disk_a/CERNBOX/WbLS-DATA/rq/v1.0.1/muon/phase1_muon_wbls_1pct_220923T1808_rq.root
/media/disk_a/CERNBOX/WbLS-DATA/rq/v1.0.1/muon/phase1_muon_wbls_1pct_220924T1753_rq.root
/media/disk_a/CERNBOX/WbLS-DATA/rq/v1.0.1/muon/phase1_muon_wbls_1pct_220925T0401_rq.root
/media/disk_a/CERNBOX/WbLS-DATA/rq/v1.0.1/muon/phase1_muon_wbls_1pct_220922T0814_rq.root
/media/disk_a/CERNBOX/WbLS-DATA/rq/v1.0.1/muon/phase1_muon_wbls_1pct_220923T2317_rq.root
```
# cherrypicker

Loading the many raw root file is difficult. Sometimes we want to cherry-picking desired events and save them to an smaller root file for later usage. This script allows one to do that given a list of `event_id`. 

Usage. In python environment, do:
```python
file_path='../data/phase1_muon_wbls_1pct_220921T1351.root'
user_event_id = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
cherrypicking(file_path, user_event_id, 'small.root')
```

# Print Binary Info 
Sometimes we want to inspect the raw binary from DAQ software. 

Usage. After setting enviromental variables, do:
```bash
python print_binary_info.py /path/to/raw_binary_file
```

Alternatively, just use `xxd` which is very useful by itself. For the manual, see:
```
xxd --help
```


# RatDB file reader
A python script that reads .ratdb (.geo) file as dictionary.

Usage. In python kernel, do
```python
from ratdb_reader import RatDBReader

r = RatDBReader(file_path=/path/to/your/file.ratdb)
```
That's it. The data are saved in `r.tables`. See `test()` example how to access it.

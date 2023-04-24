"""
Update:
    23-04-24, X. Xiang: create this script from colab notebook

We track HV supply's output voltage (VMon) and current (IMon) via GECO's logging. 
This script convert the GEGO log file to csv file. 
The csv file will be written to the same directory.

Example GECO log files:
    ### [2019-01-28T09:03:08]: [sy5527lc] bd [1] ch [4] par [VMon] val [23.78];                                                                                                                                              
    ### [2019-01-28T09:03:15]: [sy5527lc] bd [1] ch [7] par [IMon] val [1.67485];  

Usage:
    python log2csv.py \path\to\your\file.log
"""


import re
import numpy as np
from datetime import datetime
import pandas as pd
import os
import sys

import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)

class GECOLogConverter():
  def __init__(self) -> None:
    pass

  def convert_to_csv(self, file_name):
    self.filename=file_name
    self.load_data()
    self.write()

  def ParseLine(self, line):
    words = line.split()
    ### example line for sy5527lc power supply:
    ### [2019-01-28T09:03:08]: [sy5527lc] bd [1] ch [4] par [VMon] val [23.78];
    ### [2019-01-28T09:03:15]: [sy5527lc] bd [1] ch [7] par [IMon] val [1.67485]; 
    timestamp_str = words[0].replace("[","").replace("]:","")
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
    board_id   = int(words[3].replace("[","").replace("]",""))
    ch_id       = int(words[5].replace("[","").replace("]",""))
    par_name     = words[7].replace("[","").replace("]","")
    value         = float(words[9].replace("[","").replace("];",""))
    return timestamp,board_id, ch_id,par_name,value

  def load_data(self):
    filename=self.filename
    data_dict = {
        'timestamp': [] , 
        'ch_id': [],
        'par_name':[], 
        'par_value':[]
        }
    with open(filename) as file:
      lines = file.readlines()
      lines = [line.rstrip() for line in lines]
      counter=0
      for line in lines:
        try:
          timestamp, board_id, ch_id, par_name, value = self.ParseLine(line)
        except:
          print(line)
          continue
        new_row={'timestamp': timestamp, 'ch_id': id, 'par_name': par_name, 'par_value': value}
        data_dict['timestamp'].append(timestamp)
        data_dict['ch_id'].append(board_id*100 + ch_id)
        data_dict['par_name'].append(par_name)
        data_dict['par_value'].append(value)
        counter += 1
      self.n_entries = counter
      self.df = pd.DataFrame(data_dict)

  def write(self):
    ofname = self.filename[:-4]+'.csv'
    self.df.to_csv(ofname, date_format='%Y-%m-%dT%H:%M:%S')



if len(sys.argv)==2:
  file_path=str(sys.argv[1])
  cvt = GECOLogConverter()
  cvt.convert_to_csv(file_path)
else:
  print("ERROR: one argument allowed.")

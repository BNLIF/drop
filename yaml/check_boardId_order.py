"""
A simple script to check the boardId_order --- just print a few

Usage:
python check_boardId_order.py path/to/raw/data
"""


import sys
sys.path.append("../") # go to parent dir
from caen_reader import RawDataFile

raw_file_path = str(sys.argv[1])

data_file = RawDataFile(raw_file_path)
for i in range(6):
    trigger = data_file.getNextTrigger()
    if trigger is None:
        break
    print(trigger.boardId)

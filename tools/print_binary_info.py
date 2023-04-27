"""
A script to inspect binary file.

> **__Note__**: Alternatively, you can use xxd to look at binary file. Try: `xxd -h`

Usage:
    python print_binary_info.py /path/to/raw_binary_file
"""
import os
import sys

# Note: run setup.sh to get environemtal variables
src_path = os.environ['SOURCE_DIR']
sys.path.append(src_path)
from caen_reader import RawDataFile

if_path=str(sys.argv[1])


n_boards=int(input("Enter an integer for the number of boards:"))
tmp=input("Enter a bool for ETTT flag (True or False)?")
if tmp.lower()=='true' or tmp.lower()=='t':
    ETTT_flag=True
else:
    ETTT_flag=False

print("haha", ETTT_flag)

raw_data_file = RawDataFile(if_path, n_boards, ETTT_flag=ETTT_flag)
width=9
prev_ttt=0
for i in range(200):
    trigger = raw_data_file.getNextTrigger()
    if trigger is None:
        print("Done")
        break
    if i==0:
        print("recordLen:", raw_data_file.recordLen) # read one trigger to know recordLen
        print('%s\t%s\t%s\t%s\t%s' % ('i'.ljust(width), "event_id".ljust(width), "boardId".ljust(width), 'TTT'.ljust(width), 'delta_ttt'.ljust(width) ))
    delta_ttt = trigger.triggerTimeTag - prev_ttt
    print('%s\t%s\t%s\t%s\t%s' % (i, trigger.eventCounter, trigger.boardId, trigger.triggerTimeTag, delta_ttt))
    # for ch, val in trigger.traces.items():
    #    print(ch, len(val) )
    prev_ttt = trigger.triggerTimeTag

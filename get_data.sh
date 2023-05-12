#!/bin/bash

########################
# Functions:
# 1. This script transfer data from HothDAQ to MVD
# 2. This script convert binary into root

# Usage:
#     bash get_data.sh
#########################


#======================================
# GLOBAL PARAMETERS (you don't need to change it very often)
DAQ_DIR=/home/rootless/ToolApplication
GECO_DIR=/home/rootless/GECO_Logging
MVD_DIR=/media/disk_a/BNLBOX/WbLS-DATA
DAQ_USER=rootless
DAQ_IP=130.199.33.252
#======================================

echo "Enter an integer for run type (0: muon, 1: led, 2: geco)"
read RUN_TYPE

# note:
#     muon stores muon data
#     calibration stores led, alpha lightbulb, ...
#     debug store test data
#     [create your own]

DO_CSV=0
DO_ROOTER=0
if [ $RUN_TYPE -eq 2 ]; then
    echo "Do you want to convert geco log to csv file (1: yes, 0: no)?"
    read DO_CSV
else
    echo "Which sub-directory do you want to store the data? String options: muon, calibration, debug (mkdir yours if needed)"
    echo "Hint: muon stores good muon data; calibration stores led, alpha lightbulb. etc...; debug stores test data"
    read MVD_SUB_FOLDER
    
    echo "Do you want to run rooter (1: yes, 0: no)?"
    read DO_ROOTER
fi

echo "Enter an integer for the date (0: today; -1 yesterday; -2: 2 days ago ...)"
read d
DATE=$(date -d "$d day" '+%y%m%d')
echo "Start transfering data taken on $DATE"

function transfer_data() {
    if [ $RUN_TYPE -eq 1 ]; then
	output_dir=${MVD_DIR}/raw_binary/${MVD_SUB_FOLDER}
      	scp ${DAQ_USER}@${DAQ_IP}:${DAQ_DIR}/*led_*${DATE}*.bin $output_dir
	find ${output_dir}/*led_*${DATE}*.bin -type f > tmp.list
    fi

    if [ $RUN_TYPE -eq 0 ]; then
	output_dir=${MVD_DIR}/raw_binary/${MVD_SUB_FOLDER}
	scp ${DAQ_USER}@${DAQ_IP}:${DAQ_DIR}/*muon_*${DATE}*.bin $output_dir
	find ${output_dir}/*muon_*${DATE}*.bin -type f > tmp.list
    fi

    if [ $RUN_TYPE -eq 2 ]; then
	output_dir=${MVD_DIR}/db/geco
	scp ${DAQ_USER}@${DAQ_IP}:${GECO_DIR}/*IMon_*${DATE}*.log $output_dir
	find ${output_dir}/*IMon_*${DATE}*.log -type f > tmp.list
    fi
    
}

function run_rooter() {
    if [ $RUN_TYPE -eq 1 ]; then
	output_dir=${MVD_DIR}/raw_root/${MVD_SUB_FOLDER}/
	while read fpath; do
	    case "$fpath" in \#*) continue ;; esac
	    echo " "
	    echo "processing $fpath ..."
	    python src/raw_data_rooter.py --if_path=${fpath} --output_dir=${output_dir}
	done < tmp.list
    fi

    if [ $RUN_TYPE -eq 0 ]; then
	output_dir=${MVD_DIR}/raw_root/${MVD_SUB_FOLDER}
	while read fpath; do
	    case "$fpath" in \#*) continue ;; esac
	    echo " "
	    echo "processing $fpath ..."
	    python src/raw_data_rooter.py --if_path=${fpath} --output_dir=${output_dir}
	done < tmp.list
    fi
}

function run_log2csv() {
    output_dir=${MVD_DIR}/db/geco/
    while read fpath; do
	case "$fpath" in \#*) continue ;; esac
	echo " "
	echo "processing $fpath ..."
	python tools/log2csv.py ${fpath}
    done < tmp.list
}

# execute the transfer functions
transfer_data

# execute the rooter
if [ $DO_ROOTER -eq 1 ]; then
    source env/bin/activate
    run_rooter
fi

if [ $DO_CSV -eq 1 ]; then
    source env/bin/activate
    run_log2csv
fi

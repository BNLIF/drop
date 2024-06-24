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
#DAQ_DIR=/home/rootless/ToolApplication
DAQ_DIR=/home/baldoni/BNLDAQ
GECO_DIR=/home/rootless/GECO_Logging
#MVD_DIR=/media/disk_a/BNLBOX/WbLS-DATA
MVD_DIR=/media/disk_e/30t-DATA
DAQ_USER=baldoni
DAQ_IP=130.199.82.231
#======================================

echo "Enter a run type (muon, alpha, led, geco)"
read RUN_TYPE

if [ $RUN_TYPE != "geco" ]; then
    echo "Do you want to transfer temperature data? (1: yes, 0: no)"
    read TRANSFER_TEMP
fi
echo "Enter a run phase (phase0, phase1, phase2, phase3)"
read RUN_PHASE

# note:
#     muon stores muon data
#     calibration stores led, alpha lightbulb, ...
#     debug store test data
#     alpha stores alpha lightbulb
#     [create your own]

DO_CSV=0
DO_ROOTER=0
if [ $RUN_TYPE = "geco" ]; then
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
    if [ $RUN_TYPE != "geco" ]; then
		output_dir=${MVD_DIR}/raw_binary/
		scp -o ControlPath=bgconn ${DAQ_USER}@${DAQ_IP}:${DAQ_DIR}/all_pmt_test_*${DATE}*.bin $output_dir
		find ${output_dir}/all_pmt_test_*${DATE}*.bin -type f > tmp.list
		if  [ $TRANSFER_TEMP -eq 1 ]; then
			output_dir=${MVD_DIR}/temp_data/
			scp -o ControlPath=bgconn ${DAQ_USER}@${DAQ_IP}:${DAQ_DIR}/all_pmt_test_*${DATE}*_temp*.txt $output_dir
		fi
  else
		output_dir=${MVD_DIR}/db/geco
		scp -o ControlPath=bgconn ${DAQ_USER}@${DAQ_IP}:${GECO_DIR}/*IMon_*${DATE}*.log $output_dir
		find ${output_dir}/*IMon_*${DATE}*.log -type f > tmp.list
    fi
    
}

function run_rooter() {

	output_dir=${MVD_DIR}/raw_root/
	while read fpath; do
	    case "$fpath" in \#*) continue ;; esac
	    echo " "
	    echo "processing $fpath ..."
	    python src/raw_data_rooter_30t.py --if_path=${fpath} --output_dir=${output_dir}
	done < tmp.list
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
ssh -fMNS bgconn -o ControlPersist=yes ${DAQ_USER}@${DAQ_IP}
transfer_data
ssh -S bgconn -O exit -

# execute the rooter
if [ $DO_ROOTER -eq 1 ]; then
    source drop_env/bin/activate
    run_rooter
fi

if [ $DO_CSV -eq 1 ]; then
    source drop_env/bin/activate
    run_log2csv
fi

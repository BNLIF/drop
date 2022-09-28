#!/bin/bash

# This is just a bash script running many jobs in series
#
# Usage:
# . run_many.sh file_list.txt
#
# where file_list.txt is just a collection of file path

#======================================
# Run Parameters
do_raw_data_rooter=0
do_run_drop=0
do_dq_offline_monitor=1
drop_version=v1.0.1
subdir=muon
config_file=config.yaml
#====================================== 

if [ $do_raw_data_rooter -eq 1 ]; then
    file_path=$1
    output_dir=/media/disk_a/CERNBOX/WbLS-DATA/raw_root/${subdir}/
    while read fpath; do
	case "$fpath" in \#*) continue ;; esac
	echo " "
	echo "processing $fpath ..."
	python src/raw_data_rooter.py --if_path=${fpath} --output_dir=${output_dir}
    done < $file_path
fi


if [ $do_run_drop -eq 1 ]; then
    file_path=$1
    output_dir=/media/disk_a/CERNBOX/WbLS-DATA/rq/${drop_version}/${subdir}
    mkdir -p $output_dir
    while read fpath; do
	case "$fpath" in \#*) continue ;; esac
	echo " "
	echo "processing $fpath ..."
	python src/run_drop.py -i ${fpath} -c yaml/${config_file} --output_dir=${output_dir}
    done < $file_path
fi


if [ $do_dq_offline_monitor -eq 1 ]; then
    output_dir=/media/disk_a/CERNBOX/WbLS-DATA/dqom/${drop_version}/${subdir}
    mkdir -p $output_dir
    file_path=$1
    while read fpath; do
	case "$fpath" in \#*) continue ;; esac
	echo " "
	echo "processing $fpath ..."
	python tools/dqom.py ${fpath} ${output_dir}
    done < $file_path
fi

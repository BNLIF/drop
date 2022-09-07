#!/bin/bash

do_raw_data_rooter=0
do_run_drop=1

if [ $do_raw_data_rooter -eq 1 ]; then
    file_path=$1
    output_dir=/media/disk_a/CERNBOX/WbLS-DATA/raw_root/muon/
    while read fpath; do
	case "$fpath" in \#*) continue ;; esac
	echo " "
	echo "processing $fpath ..."
	python src/raw_data_rooter.py --if_path=${fpath} --output_dir=${output_dir}
    done < $file_path
fi


if [ $do_run_drop -eq 1 ]; then
    file_path=$1
    output_dir=/media/disk_a/CERNBOX/WbLS-DATA/rq/muon

    while read fpath; do
	case "$fpath" in \#*) continue ;; esac
	echo " "
	echo "processing $fpath ..."
	python src/run_drop.py -i ${fpath} -c yaml/config.yaml --output_dir=${output_dir}
    done < $file_path
fi

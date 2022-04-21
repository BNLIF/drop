#!/bin/bash

do_raw_data_rooter=1
do_run_drop=0

if [ $do_raw_data_rooter -eq 1 ]; then
    file_path=$1
    output_dir=/media/disk_a/CERNBOX/WbLS-DATA/raw_root/phase0

    while read fpath; do
	echo " "
	echo "processing $fpath ..."
	python src/raw_data_rooter.py --if_path=${fpath} --output_dir=${output_dir}
	echo ""
    done < $file_path
fi


if [ $do_run_drop -eq 1 ]; then
    echo "to do"
fi

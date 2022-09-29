#!/bin/bash

# This is just a bash script running many jobs in series
#
# Usage:
# . run_many.sh file_list.txt
#
# where file_list.txt is just a collection of file path

#======================================
# Run Parameters
run_script_option=0 #0: run all; 1: run raw_data_rooter.py; 2: run_drop.py; 3: dqom.py
drop_version=v1.0.1
subdir=muon
config_file=config.yaml
#====================================== 

function do_raw_data_rooter() {
    local file_path=$1
    output_dir=/media/disk_a/CERNBOX/WbLS-DATA/raw_root/${subdir}/
    while read fpath; do
	case "$fpath" in \#*) continue ;; esac
	echo " "
	echo "processing $fpath ..."
	python src/raw_data_rooter.py --if_path=${fpath} --output_dir=${output_dir}
    done < $file_path
}

function do_run_drop() {
    local file_path=$1
    output_dir=/media/disk_a/CERNBOX/WbLS-DATA/rq/${drop_version}/${subdir}
    mkdir -p $output_dir
    while read fpath; do
	case "$fpath" in \#*) continue ;; esac
	echo " "
	echo "processing $fpath ..."
	python src/run_drop.py -i ${fpath} -c yaml/${config_file} --output_dir=${output_dir}
    done < $file_path
}

function do_dqom() {
    local file_path=$1
    output_dir=/media/disk_a/CERNBOX/WbLS-DATA/dqom/${drop_version}/${subdir}
    mkdir -p $output_dir
    file_path=$1
    while read fpath; do
	case "$fpath" in \#*) continue ;; esac
	echo " "
	echo "processing $fpath ..."
	python tools/dqom.py ${fpath} ${output_dir}
    done < $file_path
}

file_path=$1
if [ $run_script_option -eq 1 ]; then
    do_raw_data_rooter $file_path
fi

if [ $run_script_option -eq 2 ]; then
    do_run_drop $file_path
fi

if [ $run_script_option -eq 3 ]; then
    do_dqom $file_path
fi

if [ $run_script_option -eq 0 ]; then
    tmp=$(pwd)/tmp.txt
    cp $file_path $tmp
    do_raw_data_rooter $tmp
    
    sed -i -e 's/binary/root/g' $tmp
    sed -i -e 's/.bin/.root/g' $tmp
    do_run_drop $tmp

    olddir="raw_root/${subdir}"
    newdir="rq/${drop_version}/${subdir}"
    sed -i "s|$olddir|$newdir|g" $tmp
    sed -i -e 's/.root/_rq.root/g' $tmp
    do_dqom $tmp

    rm $tmp
fi

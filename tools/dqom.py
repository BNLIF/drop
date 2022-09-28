"""
DQOM stands for Data Quality Offline Monitor

It's just python script making a set of plots, and save them to a directory

Usage:
0. Enter eniv
2. python dqom.py [path/to/rq/file] [output_dir]
"""


import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import re
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import os

def extract_datetime_from_str(s):
    """
    Extract datatime from a str. The datetime must follow the fixed format:
    YYmmddTHHMM
    """
    match = re.search(r'\d{6}T\d{4}', s)
    try:
        dt = datetime.strptime(match.group(), '%y%m%dT%H%M')
        return dt
    except ValueError:
        print('Fail finding the datetime string from path: %s' % s)
        
def plot_channel_npe(file_path, output_dir):
    start_dt = extract_datetime_from_str(file_path)
    with uproot.open(file_path) as f:
        rq = f['event'].arrays(library='np')
        ch_id = rq['ch_id'][0]
        nch = len(ch_id)
        ncol=5
        nrow=nch//ncol+1
        fig, ax = plt.subplots(nrow, ncol, figsize=[4*ncol,2.7*nrow])
        ax = ax.flatten()
        t_minute=rq['event_ttt']*8e-9/60
        tmax = np.max(t_minute)
        tmin = np.min(t_minute)
        nbinx = int((tmax-tmin)/5+0.5) # every 5 minutes a bin
        for r, ch in enumerate(ch_id):
            ch_mask=(rq['ch_id']==ch)
            ch_roi1_area_pe=rq['ch_roi1_area_pe'][ch_mask].flatten()
            h0 = ax[r].hist2d(t_minute, ch_roi1_area_pe, bins=[nbinx, 50], range=((tmin,tmax),(0, 50)), norm=colors.LogNorm(), cmap='jet');
            ax[r].set_xlabel('Time elapsed since run start [min]', fontsize=12)
            ax[r].set_ylabel('Channel Npe', fontsize=12)
            ax[r].set_title("ch_id=%d" % ch)
        plt.tight_layout()
        directory="%s/ChannelNpeTrend" % output_dir
        if not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig('%s/%s.pdf' % (directory, start_dt.strftime("%y%m%dT%H%M")))

def plot_channel_noise(file_path, output_dir):
    start_dt = extract_datetime_from_str(file_path)
    with uproot.open(file_path) as f:
        rq = f['event'].arrays(library='np')
        ch_id = rq['ch_id'][0]
        ncol=5
        nch = len(ch_id)
        nrow=nch//ncol+1
        fig, ax = plt.subplots(nrow, ncol, figsize=[4*ncol,2.7*nrow])
        ax = ax.flatten()
        t_minute=rq['event_ttt']*8e-9/60
        tmax = np.max(t_minute)
        tmin = np.min(t_minute)        
        nbinx = int((tmax-tmin)/5+0.5) # every 5 minutes a bin 
        for r, ch in enumerate(ch_id):
            ch_mask=(rq['ch_id']==ch)
            ch_roi0_std_pe=rq['ch_roi0_std_pe'][ch_mask].flatten()
            h0 = ax[r].hist2d(t_minute, ch_roi0_std_pe, bins=[nbinx, 50], range=((tmin,tmax),(0, 0.5)), 
                              norm=colors.LogNorm(), cmap='jet');
            ax[r].set_xlabel('Time elapsed since run start [min]', fontsize=12)
            ax[r].set_ylabel('Channel Baseline Std [PE/ns]', fontsize=12)
            ax[r].set_title("ch_id=%d" % ch)
        plt.tight_layout()
    directory="%s/ChannelBaselineTrend" % output_dir
    if not os.path.exists(directory):
        os.makedirs(directory)
    plt.savefig('%s/%s.pdf' % (directory, start_dt.strftime("%y%m%dT%H%M")))

        
if __name__ == "__main__":
    if len(sys.argv)==3:
        plot_channel_npe(str(sys.argv[1]), str(sys.argv[2]))
        plot_channel_noise(str(sys.argv[1]), str(sys.argv[2]))
    else:
        sys.exit("Wrong number of input argument")

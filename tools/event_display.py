"""
Simple Event Display

PYTHONPATH is specified in setup.sh
"""
import os
import sys
import numpy as np
import matplotlib.pylab as plt
import uproot
import awkward as ak

src_path = os.environ['PYTHONPATH']
sys.path.append(src_path)

from utilities import generate_colormap
from run_drop import RunDROP

class Args:
    start_id = 0
    end_id = 99999999
    output_dir=""
    if_path=""
    yaml= '%s/../yaml/config.yaml' % src_path


class EventDisplay():
    def __init__(self, raw_data_path):

        self.args = Args()
        self.args.if_path=raw_data_path
        self.run = RunDROP(self.args)

    def grab_events(self, event_id):
        """
        Grab raw data matching event_id.

        Args:
        - event_id: int or list. ex. [1000, 1001, 3000, 30]. The grabbed events
        will be sorted in increasing order.
        """
        if np.isscalar(event_id):
            event_id = [event_id]
        self.event_id_list = event_id

        self.wfm_list = []
        self.pf_list = []
        batch_list = uproot.iterate('%s:daq' % self.args.if_path, step_size=1000)
        for batch in batch_list:
            arr = batch.event_id.to_numpy()
            mask = np.isin(arr, event_id)
            run = self.run
            run.process_batch(batch[mask], None)
            self.wfm_list.append(run.wfm_list)
            self.pf_list.append(run.pf_list)
        self.wfm_list = [item for sublist in self.wfm_list for item in sublist]
        self.pf_list = [item for sublist in self.pf_list for item in sublist]

    def display_summed_waveform(self):
        '''
        ch: string, ex. b1_ch0, sum. Default: None (all)
        '''
        i=0
        fig = plt.figure(figsize=[8,4])
        plt.subplot(111)
        a = self.wfm_list[i].amplitude['sum']
        plt.plot(a, label='summed channel')
        plt.plot(np.zeros(len(a)), '--', color='gray', label='flat baseline')
        plt.legend(loc=0)
        plt.title('event_id=%d' % self.event_id_list[i])
        ymin, ymax = plt.ylim()
        plt.ylim(ymax=ymax + (ymax-ymin)*.15)
        plt.xlabel('Samples')
        plt.ylabel('ADC')
        plt.grid(linewidth=0.5, alpha=0.5)
        plt.show()

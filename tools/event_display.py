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
import re

# Note: run setup.sh to get environemtal variables
src_path = os.environ['SOURCE_DIR']
yaml_path = os.environ['YAML_DIR']
sys.path.append(src_path)

from utilities import generate_colormap
from run_drop import RunDROP

class Args:
    start_id = 0
    end_id = 99999999
    output_dir=""
    if_path=""
    yaml= '%s/config.yaml' % yaml_path


class EventDisplay():
    def __init__(self, raw_data_path):

        self.args = Args()
        self.args.if_path=raw_data_path
        self.run = RunDROP(self.args)
        self.grabbed_event_id = []

        # useful to give user hints
        self.min_event_id = 999999999
        self.max_event_id = 0

        # beautify
        # self.cmap = generate_colormap(16)
        self.cmap=plt.get_cmap('tab20')

    def grab_events(self, wanted_event_id):
        """
        Grab raw data matching event_id. Process them using RunDrop.

        Args:
            wanted_event_id: int or list. ex. [1000, 1001, 3000, 30]. The grabbed events
        will be sorted in that order.

        Return:
            int, length of events grabbed
        """
        if isinstance(wanted_event_id, int):
            wanted_event_id = [wanted_event_id]
        elif isinstance(wanted_event_id, list):
            pass
        else:
            print("ERROR: wanted_event_id must be either int of list of int")
            return None

        self.wfm_list = []
        self.pf_list = []
        batch_list = uproot.iterate('%s:daq' % self.args.if_path, step_size=1000)
        for batch in batch_list:
            arr = batch.event_id.to_numpy()
            mask = np.isin(arr, wanted_event_id)
            run = self.run
            run.process_batch(batch[mask], None)
            self.wfm_list.append(run.wfm_list)
            self.pf_list.append(run.pf_list)

            # record min and max event_id for hints
            self.min_event_id = np.min([self.min_event_id, np.min(arr)])
            self.max_event_id = np.max([self.max_event_id, np.max(arr)])

        self.wfm_list = [item for sublist in self.wfm_list for item in sublist]
        self.pf_list = [item for sublist in self.pf_list for item in sublist]
        self.grabbed_event_id = [wfm.event_id for wfm in self.wfm_list]
        if not self.grabbed_event_id:
            print('Info: your wanted events are not found.')
            print('Hint: event_id is in this range [%d, %d]' % (self.min_event_id, self.max_event_id))
        return len(self.grabbed_event_id)

    def display_waveform(self, event_id, ch, baseline_subtracted=True, no_show=False):
        """
        Plot waveform, for selected channel(s), summed channel, or all channels

        Args:
            event_id (int): the event you want to see
            ch (str or list): the channel(s) you want to see. If ch is str type,
                for example, `b1_ch10`, plot that individual channel. if `ch=sum`,
                plot the summed channel; if `ch=all` for plot all channels at once.
                if ch is a list, plot that list.
            baseline_subtracted (bool): plot baseline_subtracted waveform or not.
                summed channel waveform is only available in baseline subtracted
                form, while others have this options.
            no_show (bool): draw option
        """
        if isinstance(event_id, int):
            if event_id in self.grabbed_event_id:
                i = self.grabbed_event_id.index(event_id)
            else:
                n = self.grab_events(event_id)
                if n==1:
                    i=0
                else:
                    return None
        else:
            print('ERROR: event_id must be int')
            return None

        if isinstance(ch, str):
            if ch == 'sum' or ch == 'summed':
                self.__display_summed_waveform(i, no_show)
            elif ch == 'all':
                if baseline_subtracted==True:
                    self.__display_all_ch_raw_waveform(i, no_show)
                else:
                    self.__display_all_ch_waveform(i, no_show)
            else:
                if ch[0:3] != 'adc_':
                    # sometimes user forget the prefix adc_
                    ch = 'adc_' + ch
                if ch not in self.run.ch_names:
                    print("ERROR: ch is not found in active ch_names")
                    print('Hint: active ch names are:', self.run.ch_names)
                    return None
                if baseline_subtracted==True:
                    self.__display_ch_waveform(i, ch, no_show)
                else:
                    self.__display_ch_raw_waveform(i, ch, no_show)
        elif isinstance(ch, list):
            pass # to do
        else:
            print("ERROR: ch variable type is not recognized.")
            return None

    def __display_summed_waveform(self, i, no_show=False):
        fig = plt.figure(figsize=[8,4])
        plt.subplot(111)
        a = self.wfm_list[i].amplitude['sum']
        plt.plot(a, label='summed channel')
        plt.plot(np.zeros(len(a)), '--', color='gray', label='flat baseline')
        plt.legend(loc=0)
        plt.title('event_id=%d' % self.grabbed_event_id[i])
        ymin, ymax = plt.ylim()
        plt.ylim(ymax=ymax + (ymax-ymin)*.15)
        plt.xlabel('Samples')
        plt.ylabel('ADC')
        plt.grid(linewidth=0.5, alpha=0.5)
        if no_show==False:
            plt.show()
        return None

    def __display_ch_waveform(self, i, ch, no_show=False):
        fig = plt.figure(figsize=[8,4])
        a = self.wfm_list[i].amplitude[ch]
        plt.plot(a, label=ch[4:]) # remove adc_ from ch names
        plt.plot(np.zeros(len(a)), '--', color='gray', label='flat baseline')
        plt.legend(loc=0)
        plt.title('event_id=%d' % self.grabbed_event_id[i])
        ymin, ymax = plt.ylim()
        plt.ylim(ymax=ymax + (ymax-ymin)*.15)
        plt.xlabel('Samples')
        plt.ylabel('ADC')
        plt.grid(linewidth=0.5, alpha=0.5)
        if no_show==False:
            plt.show()

    def __display_ch_raw_waveform(self, i, ch, no_show=False):
        fig = plt.figure(figsize=[8,4])
        a = self.wfm_list[i].raw_data[ch].to_numpy()
        plt.plot(a, label=ch[4:])
        plt.legend(loc=0)
        plt.title('event_id=%d' % self.grabbed_event_id[i])
        ymin, ymax = plt.ylim()
        plt.ylim(ymax=ymax + (ymax-ymin)*.15)
        plt.xlabel('Samples')
        plt.ylabel('ADC')
        plt.grid(linewidth=0.5, alpha=0.5)
        if no_show==False:
            plt.show()

    def __get_active_board_id(self):
        """
        which boardId is available? Return a set of int.

        ex. adc_b1_ch1, as far as board range from 0-9, this is okay
        """
        active_board_id = set()
        for ch in self.run.ch_names:
            active_board_id.add(int(int(ch[5])))
        return active_board_id

    def __display_all_ch_waveform(self, i, no_show=False):

        active_board_id = self.__get_active_board_id()
        n_boards = self.run.n_boards
        fig, axes = plt.subplots(n_boards, 1, figsize=[8,4*n_boards], sharex=True)

        for b, b_id in enumerate(active_board_id):
            for ch in self.run.ch_names:
                if int(ch[5]) == b_id:
                    #ch_id is the end digit
                    ch_id = int(re.match('.*?([0-9]+)$', ch).group(1))
                    a = self.wfm_list[i].amplitude[ch]
                    axes[b].plot(a, label=ch[7:], color=self.cmap.colors[ch_id])
            axes[b].plot(np.zeros(len(a)), '--', color='gray', label='flat baseline')
            if b==0:
                axes[b].set_title('event_id=%d' % self.grabbed_event_id[i])
            axes[b].set_xlabel('Samples')
            axes[b].set_ylabel('ADC')
            axes[b].grid(linewidth=0.5, alpha=0.5)
            axes[b].legend(loc=0, title="board_id: %d" % b_id, ncol=2)
        if no_show==False:
            plt.show()

    def __display_all_ch_raw_waveform(self, i, no_show=False):

        active_board_id = self.__get_active_board_id()
        n_boards = self.run.n_boards
        fig, axes = plt.subplots(n_boards, 1, figsize=[8,4*n_boards], sharex=True)

        for b, b_id in enumerate(active_board_id):
            for ch in self.run.ch_names:
                if int(ch[5]) == b_id:
                    #ch_id is the end digit
                    ch_id = int(re.match('.*?([0-9]+)$', ch).group(1))
                    a = self.wfm_list[i].raw_data[ch].to_numpy()
                    axes[b].plot(a, label=ch[7:], color=self.cmap.colors[ch_id])
            if b==0:
                axes[b].set_title('event_id=%d' % self.grabbed_event_id[i])
            axes[b].set_xlabel('Samples')
            axes[b].set_ylabel('ADC')
            axes[b].grid(linewidth=0.5, alpha=0.5)
            axes[b].legend(loc=0, title="board_id: %d" % b_id, ncol=2)
        if no_show==False:
            plt.show()

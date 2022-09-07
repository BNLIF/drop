_d"""
Simple Event Display

PYTHONPATH is specified in setup.sh
"""
import os
import sys
import numpy as np
import matplotlib.pylab as plt
import matplotlib.patches as patches
import matplotlib
import uproot
import awkward as ak
import re

# Note: run setup.sh to get environemtal variables
src_path = os.environ['SOURCE_DIR']
YAML_DIR = os.environ['YAML_DIR']
sys.path.append(src_path)

from utilities import generate_colormap
from run_drop import RunDROP
from pulse_finder import PulseFinder
from yaml_reader import SAMPLE_TO_NS

class Args:
    start_id = 0
    end_id = 99999999
    output_dir=""
    if_path=""
    yaml= ''


class EventDisplay():
    def __init__(self, raw_data_path, yaml_path=None):
        """Constructor:

        EventDisplay class to visualize individual waveform. This class recyles
        the same source code in drop/src. So details such as the baseline
        subtraction, SPE normalization, accumulated integral, and pulse finder
        results are consisent with DROP --- good for making cross-checks with the
        Reduced Quality (RQ) variables.

        Usage example:
            event_display_example.ipynb.

        Args:
            raw_data_path (str): path to the raw root file
            yaml_path (str): path to the configuration yaml file (default:
                yaml/config.yaml)

        Notes:
            Since EventDisplay uses DROP source code, brand new update may break
            the main EventDispaly in the main branch. Try `event_display` branch
            which contains an older but a frozen version of DROP.
        """
        self.args = Args() # arguments needed to run DROP
        self.args.if_path=raw_data_path
        if yaml_path is None:
            self.args.yaml = '%s/config.yaml' % YAML_DIR
        else:
            self.args.yaml = yaml_path
        self.run = RunDROP(self.args)
        self.grabbed_event_id = []

        self.user_summed_channel_list=None

        # useful to give user hints
        self.min_event_id = 999999999
        self.max_event_id = 0

        # plotting logistics
        self.save_fig_flag = False
        self.save_fig_dir = './'

        # beautify
        # self.cmap = generate_colormap(16)
        #self.cmap=plt.get_cmap('tab20')
        self.user_ch_colors =['b', 'g', 'r', 'c', 'm', 'y',
        'tab:blue', 'tab:orange', 'lime', 'lightcoral', 'tab:purple', 'tab:brown',
        'tab:pink', 'tab:gray', 'navy', 'gold']
        self.fig_width=8
        self.fig_height=4
        self.xlim = None
        self.ylim = None
        self.dpi = None
        self.logy_flag = False

        # how many new figure?
        self.plot_counter = 0

    def set_user_summed_channel_list(self, user_list: list):
        """
        Set a user-defined list of channels to plot.

        Args:
            user_list (list): a list of str or a list of int

        Examples:
            For example, the following list is sum of all side channels
            user_list=[300, 301, 302, 303, 304, 305, 306, 307, 308, 309,
            310, 311, 312, 313, 314, 315]
        """
        user_list = self.run.cfg.get_ch_names(user_list)
        self.user_summed_channel_list = user_list
        return None

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

        self.wfm_list = [item for sublist in self.wfm_list for item in sublist] # flatten list
        self.pf_list = [item for sublist in self.pf_list for item in sublist]
        self.grabbed_event_id = [wfm.event_id for wfm in self.wfm_list]
        if not self.grabbed_event_id:
            print('Info: your wanted events are not found.')
            print('Hint: event_id is in this range [%d, %d]' % (self.min_event_id, self.max_event_id))
        return len(self.grabbed_event_id)

    def display_waveform(self, event_id, ch, baseline_subtracted=True, no_show=False):
        """
        Plot waveform, for individual channel, all channels, summed channel,
        or selected summed channels.

        Args:
            event_id (int): the event you want to see
            ch (str): the channel(s) you want to see. If ch is str type,
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
                self._display_summed_waveform(i, no_show)
            elif ch == 'all':
                if baseline_subtracted==False:
                    self._display_all_ch_raw_waveform(i, no_show)
                else:
                    self._display_all_ch_waveform(i, no_show)
            else:
                if ch[0:3] != 'adc_':
                    # sometimes user forget the prefix adc_
                    ch = 'adc_' + ch
                if ch not in self.run.ch_names:
                    print("ERROR: ch is not found in active ch_names")
                    print('Hint: active ch names are:', self.run.ch_names)
                    return None
                if baseline_subtracted==True:
                    self._display_ch_waveform(i, ch, no_show)
                else:
                    self._display_ch_raw_waveform(i, ch, no_show)
        elif isinstance(ch, list):
            pass # to do
        else:
            print("ERROR: ch variable type is not recognized.")
            return None

    def _display_summed_waveform(self, i, no_show=False):
        """
            Notes: function starts with _ are not meant for users to call. This
            is a python naming convention, not strictly enforced.
        """
        #plt.clf()
        fig = plt.figure(figsize=[self.fig_width,self.fig_height])
        self.plot_counter += 1
        ax1 = plt.subplot(111)

        user_list = self.user_summed_channel_list
        if user_list is None:
            a = self.wfm_list[i].amp_pe['sum']
        elif isinstance(user_list, list):
            if len(user_list)>0:
                a = 0
                for ch in self.wfm_list[i].amp_pe:
                    if ch in user_list:
                        a += self.wfm_list[i].amp_pe[ch]
        else:
            print('ERROR: bad user_summed_channel_list!')
        a_int = np.cumsum(a)*(SAMPLE_TO_NS) # amp_mV_int does not exist
        left_ylabel = "PE / 2ns"
        right_ylabel = 'PE'

        t = np.arange(0, len(a)*2, 2)
        ax1.plot(t, a, label='summed channel');
        ax1.plot(t, np.zeros(len(a)), '--', color='gray', label='flat baseline');
        trg_time_ns = self.wfm_list[i].trg_time_ns
        ax1.scatter(trg_time_ns, 0.01, color='orange', marker='v', label='master trigger time')
        ax1.legend(loc='upper left')
        plt.title('event_id=%d' % self.grabbed_event_id[i])
        ymin, ymax = plt.ylim()
        plt.ylim(ymax=ymax + (ymax-ymin)*.15)
        plt.ylabel(left_ylabel)
        plt.xlabel('Time [ns]')
        plt.grid(linewidth=0.5, alpha=0.5)


        ax2 = ax1.twinx()
        ax2.plot(t, a_int, color='k', label='accumulated', linewidth=1)
        ax2.legend(loc='center right')
        ax2.set_ylabel(right_ylabel)
        p = self.pf_list[i]
        if p.n_pulses>0:
            for j in range(len(p.start)):
                xy = (p.start[j]*(SAMPLE_TO_NS), 0)
                #h = np.max(a[p.start[j]:p.end[j]])
                h = p.height_sum_pe[j]
                w = (p.end[j]-p.start[j])*(SAMPLE_TO_NS)
                rect = patches.Rectangle(xy, w, h, label='pulse', linewidth=0.5,
                edgecolor='r', facecolor='none')
                ax1.add_patch(rect)

        if self.xlim is not None:
            ax1.set_xlim(self.xlim)
        if self.ylim is not None:
            ax1.set_ylim(self.ylim)
        if self.logy_flag:
            ax1.set_yscale('log')
            ax2.set_yscale('log')

        if no_show==False:
            plt.show()
        return None

    def _display_ch_waveform(self, i, ch, no_show=False):
        """
            Notes: function starts with _ are not meant for users to call. This
            is a python naming convention, not strictly enforced.
        """
        # plt.clf()
        fig = plt.figure(figsize=[self.fig_width,self.fig_height])
        self.plot_counter += 1
        ax1 = plt.subplot(111)

        if ch in self.run.cfg.non_signal_channels:
            a = self.wfm_list[i].amp_mV[ch]
            left_ylabel="mV / 2ns"
            right_ylabel="mV * ns"
        else:
            a = self.wfm_list[i].amp_pe[ch]
            left_ylabel="PE / 2ns"
            right_ylabel="PE"
        a_int = np.cumsum(a)*(SAMPLE_TO_NS) # amp_mV_int does not exist

        t = np.arange(0, len(a)*2, 2)
        ax1.plot(t, a, label=ch[4:]) # remove adc_ from ch names
        ax1.plot(t, np.zeros(len(a)), '--', color='gray', label='flat baseline')
        trg_time_ns = self.wfm_list[i].trg_time_ns
        ax1.scatter(trg_time_ns, 0.01, color='orange', marker='v', label='master trigger time')
        ax1.legend(loc='upper left')
        plt.title('event_id=%d' % self.grabbed_event_id[i])
        ymin, ymax = plt.ylim()
        plt.ylim(ymax=ymax + (ymax-ymin)*.15)
        plt.xlabel('Time [ns]')
        plt.ylabel(left_ylabel)
        plt.grid(linewidth=0.5, alpha=0.5)

        ax2 = ax1.twinx()
        ax2.plot(t, a_int, color='k', label='accumulated', linewidth=1)
        ax2.legend(loc='center right')
        plt.ylabel(right_ylabel)

        # user config
        if self.xlim is not None:
            ax1.set_xlim(self.xlim)
        if self.ylim is not None:
            ax1.set_ylim(self.ylim)
        if self.logy_flag:
            ax1.set_yscale('log')
            ax2.set_yscale('log')

        if no_show==False:
            plt.show()

    def _display_ch_raw_waveform(self, i, ch, no_show=False):
        """
            Notes: function starts with _ are not meant for users to call. This
            is a python naming convention, not strictly enforced.
        """
        #plt.clf()
        fig = plt.figure(figsize=[self.fig_width,self.fig_height])
        self.plot_counter += 1
        a = self.wfm_list[i].raw_data[ch].to_numpy()
        plt.plot(a, label=ch[4:])
        plt.legend(loc=0)
        plt.title('event_id=%d' % self.grabbed_event_id[i])
        ymin, ymax = plt.ylim()
        plt.ylim(ymax=ymax + (ymax-ymin)*.15)
        if self.xlim is not None:
            plt.xlim(self.xlim)
        plt.xlabel('Samples')
        plt.ylabel('ADC')
        plt.grid(linewidth=0.5, alpha=0.5)
        if no_show==False:
            plt.show()

    def _get_active_board_id(self):
        """
        which boardId is available? Return a set of int.

        ex. adc_b1_ch1, as far as board range from 0-9, this is okay
        """
        active_board_id = set()
        for ch in self.run.ch_names:
            active_board_id.add(int(int(ch[5])))
        return active_board_id

    def _display_all_ch_waveform(self, i, no_show=False):
        """
            Notes: function starts with _ are not meant for users to call. This
            is a python naming convention, not strictly enforced.
        """
        active_board_id = self._get_active_board_id()
        n_boards = self.run.n_boards

        fig, axes = plt.subplots(n_boards, 1, figsize=[8,4*n_boards], sharex=True)

        for b, b_id in enumerate(active_board_id):
            for ch in self.run.ch_names:
                if ch in self.run.cfg.non_signal_channels:
                    continue
                if int(ch[5]) == b_id:
                    #ch_id is the end digit
                    ch_id = int(re.match('.*?([0-9]+)$', ch).group(1))
                    a = self.wfm_list[i].amp_pe[ch]
                    t = np.arange(0, len(a)*2, 2)
                    axes[b].plot(t, a, label=ch[7:], linewidth=1, color=self.user_ch_colors[ch_id])
                    axes[b].plot(t, np.zeros(len(a)), '--', color='gray', linewidth=1)
            if b==0:
                axes[b].set_title('event_id=%d' % self.grabbed_event_id[i])
            axes[b].set_xlabel('Time [ns]')
            axes[b].set_ylabel("PE / 2ns")
            axes[b].grid(linewidth=0.5, alpha=0.5)
            axes[b].legend(loc='best', title="board_id: %d" % b_id, ncol=2, fontsize=8)
            # user config
            if self.xlim is not None:
                axes[b].set_xlim(self.xlim)
            if self.ylim is not None:
                axes[b].set_ylim(self.ylim)
        if no_show==False:
            plt.show()

    def _display_all_ch_raw_waveform(self, i, no_show=False):
        """
            Notes: function starts with _ are not meant for users to call. This
            is a python naming convention, not strictly enforced.
        """
        active_board_id = self._get_active_board_id()
        n_boards = self.run.n_boards
        fig, axes = plt.subplots(n_boards, 1, figsize=[8,4*n_boards], sharex=True)

        for b, b_id in enumerate(active_board_id):
            for ch in self.run.ch_names:
                if ch in self.run.cfg.non_signal_channels:
                    continue
                if int(ch[5]) == b_id:
                    #ch_id is the end digit
                    ch_id = int(re.match('.*?([0-9]+)$', ch).group(1))
                    a = self.wfm_list[i].raw_data[ch].to_numpy()
                    axes[b].plot(a, label=ch[7:], color=self.user_ch_colors[ch_id])
            if b==0:
                axes[b].set_title('event_id=%d' % self.grabbed_event_id[i])
            axes[b].set_xlabel('Samples')
            axes[b].set_ylabel('ADC')
            axes[b].grid(linewidth=0.5, alpha=0.5)
            axes[b].legend(loc=0, title="board_id: %d" % b_id, ncol=2)
        if no_show==False:
            plt.show()

    def _merge_dict(self, d1, d2):
        ds = [d1, d2]
        d = {}
        for k in d1.keys():
            d[k] = np.concatenate(list(d[k] for d in ds))
        return d

    def set_bottom_pmt_positions(self):
        """
        Location of PMTs, which is hard coded for now

        TODO: use tools/ratdb_reader.py, which can readin ratdb/geo file, and extract
        position from them.
        """
        # when bottom is filled with 30 PMTs, copy from ratdb
        bottom_position_30pmt = {
        "x": [381. ,  381. ,  381. ,  381. ,  190.5,  190.5,  190.5,  190.5, 190.5,  \
        190.5,  190.5,    0. ,    0. ,  0. ,    0. ,    0. , 0. ,    0. ,    0. , \
         -190.5, -190.5, -190.5, -190.5, -190.5, -190.5, -190.5, -381. , -381. , \
         -381. , -381.],
        "y": [-171.45,  -57.15,   57.15,  171.45, -342.9 , -228.6 , -114.3 , 0.,\
         114.3 ,  228.6 ,  342.9 , -400.05, -285.75, -171.45,-57.15,   57.15, \
         171.45,  285.75,  400.05, -342.9 , -228.6, -114.3 ,    0.  ,  114.3 ,  228.6 ,\
         342.9 , -171.45,  -57.15, 57.15,  171.45],
         'z': [-669.925]*30
        }
        side_position_16pmt = {
        "x": [0.] * 18,
        "y": [0.] * 18,
        "z": [200.] * 18
        }

        self.pmt_pos  = self._merge_dict(bottom_position_30pmt, side_position_16pmt)

        self.ch_to_bt_pmt_map = {
        'adc_b1_ch0': None, 'adc_b1_ch1': 1, 'adc_b1_ch2': 2, 'adc_b1_ch3': 3,
        'adc_b1_ch4': 4, 'adc_b1_ch5': 5, 'adc_b1_ch6': 6, 'adc_b1_ch7': 7,
        'adc_b1_ch8': 8, 'adc_b1_ch9': 9, 'adc_b1_ch10': 10, 'adc_b1_ch11': 11,
        'adc_b1_ch12': 12, 'adc_b1_ch13': 13, 'adc_b1_ch14': 14, 'adc_b1_ch15': 15,

        'adc_b2_ch0': 16, 'adc_b2_ch1': 17, 'adc_b2_ch2': 18, 'adc_b2_ch3': 19,
        'adc_b2_ch4': 20, 'adc_b2_ch5': 21, 'adc_b2_ch6': 22, 'adc_b2_ch7': 23,
        'adc_b2_ch8': 24, 'adc_b2_ch9': 25, 'adc_b2_ch10': 26, 'adc_b2_ch11': 27,
        'adc_b2_ch12': 28, 'adc_b2_ch13': 29, 'adc_b2_ch14': 30, 'adc_b2_ch15': None,
        }

        self.ch_to_side_pmt_map = {}
        return None


    def get_bottom_pmt_hit_pattern(self, event_id, start_ns=0, end_ns=100):
        """
        Get the bottom PMT hit patterns

        Args:
            event_id (int): the event you want
            start_ns (int): the first ns to include
            end_ns (int): The end ns. Open end conv, ex: [start_ns, end_ns).

        Notes:
            WORK IN PROGRESS. THIS FUNCTION HAS NOT BEEN TESTED.

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

        if start_ns >= end_ns or start_ns <0:
            print("ERROR: start=%d and end=%d does not make sense." % (start_ns, end_ns))
            return None

        start = start_ns//2
        end = end_ns//2

        # get pmt coordinates
        self.set_bottom_pmt_positions()
        pmt_pos_x = self.pmt_pos['x']
        pmt_pos_y = self.pmt_pos['y']
        pmt_pos_z = self.pmt_pos['z']

        # select channels to bottom pmt
        bt_pmt_ch = []
        for ch in self.run.ch_names:
            if ch in self.run.cfg.non_signal_channels:
                continue
            if '_b3' in ch:
                continue
            bt_pmt_ch.append(ch)


        # calcualte integral from start to end
        a_int = self.wfm_list[i].amp_pe_int
        area = {}
        area_max = 1
        for ch in bt_pmt_ch:
            val = a_int[ch][end]-a_int[ch][start]
            area[ch] = val
            area_max = np.max([val, area_max])

        # define color
        cmap = plt.cm.jet
        norm = matplotlib.colors.Normalize(vmin=0, vmax=area_max)

        # draw active PMT whose color scale with integral
        draw_area = 94
        fig, ax = plt.subplots(figsize=[5,5])
        for ch in bt_pmt_ch:
            pmt_id = self.ch_to_bt_pmt_map[ch]
            x=pmt_pos_x[pmt_id]
            y=pmt_pos_y[pmt_id]
            z=pmt_pos_z[pmt_id]
            if z>0:
                continue
            plt.scatter(x,y,color=cmap(norm(area[ch])), s=draw_area, marker='o')
        circle1 = plt.Circle((0, 0), radius=500.38, color='gray', fill=False)
        ax.add_patch(circle1)

        # draw bottom PMT as circle
        for i in range(len(pmt_pos_x)):
            x = pmt_pos_x[i]
            y = pmt_pos_y[i]
            z = pmt_pos_z[i]
            if z>0:
                continue
            circle2 = plt.Circle((x, y), radius=25.4, color='gray', fill=False)
            ax.add_patch(circle2)
        ax.set_aspect(1)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])  # only needed for matplotlib < 3.1

        # draw paddle
        plt.scatter(75, 75, color='black', s=draw_area, marker='x')

        plt.xlabel('x [mm]')
        plt.ylabel('y [mm]')
        plt.title('Bottom PMTs')
        fig.colorbar(sm)
        plt.show()

from numpy import nan, zeros, fromfile, dtype, uint32, uint64
import numpy as np
from os import path
import matplotlib.pylab as plt

# =============================================
# ============= Data File Class ===============
# =============================================

class RawDataFile:
    def __init__(self, fileName, n_boards, ETTT_flag=False, DAQ_Software='ToolDAQ'):
        """
        Initializes the dataFile instance to include the fileName, access time,
        and the number of boards in the file. Also opens the file for reading.

        Args:
            fileName: str. the path to binary file.
            n_boards: int, number of boards
            ETTT_flag: bool (default: False)
            DAQ_Software: str. (options: LabVIEW, ToolDAQ, default to ToolDAQ)
        """
        self.fileName = path.abspath(fileName)
        self.file = open(self.fileName, 'rb')
        self.ETTT_flag=ETTT_flag # Extended TTT is in use?
        self.recordLen = 0
        self.oldTimeTag = {}
        self.timeTagRollover = {}
        for i in range(n_boards):
            self.oldTimeTag[i+1]=0
            self.timeTagRollover[i+1]=0
        self.DAQ_Software = DAQ_Software
        self.trigger_counter=0
        self.event_counter=0
        self.verbosity=1
        
    '''
    def get_next_n_words(self, n_words=4, skip_word=0xffffffff):
        """
        CAEN binary is 32-bit (4-byte) per word. Get next n words from binary file.

        Args:
            n_words: int
            skip_word: skip this word during the read. Read next from file and append. 
        """
        if self.DAQ_Software=='LabVIEW':
            order_type='>u4'
        else:
            order_type='<u4'
        try:
            w = fromfile(self.file, dtype=order_type, count=n_words)
            n_skip = sum(w==skip_word)
            if n_skip>0:
                w=w[w!=skip_word]
                w = np.append(w, fromfile(self.file, dtype=order_type, count=n_skip))
            return w
        except ValueError:
            return None
    '''
    def get_next_n_words(self, n_words=4, byte_offset=0):
        """
        CAEN binary is 32-bit (4-byte) per word. Get next n words from binary file.

        Args:
            n_words: int
            skip_word: skip this word during the read. Read next from file and append.
        """
        if self.DAQ_Software=='LabVIEW':
            order_type='>u4'
        else:
            order_type='<u4'
        try:
            w = fromfile(self.file, dtype=order_type, count=n_words, offset=byte_offset)
            #n_skip = sum(w==skip_word)
            #if n_skip>0:
            #    w=w[w!=skip_word]
            #    w = np.append(w, fromfile(self.file, dtype=order_type, count=n_skip))
            return w
        except ValueError:
            return None

    def get_next_byte(self):
        """
        Read only the next byte in the file
        """
        try:
            b = fromfile(self.file, dtype='<u1', count=1)
            return b[0]
        except ValueError:
            return None

    def decode_V1740_data(self, words):
        """
        The V1740 outputs data 12 bits at a time, but the data can't be read out in 12-bit words.
        The data also gets read out channel by channel in 3 sample increments
        (ch0s0, ch0s1, ch0s2, ch1s0, ch1s1, etc)
        So we must decode the data 9 32-bit words at a time.

        Returns 24 samples (3 for each channel in group).
        """
        # Make sure number of words is 9
        if (len(words) != 9):
            print("Number of words read must be 9")
            print(len(words))
            return None
        samps = []
        for i in range(len(words)//3):
            s0 = (words[i*3] & 0x00000FFF)
            s1 = (words[i*3] & 0x00FFF000) >> (3*4)
            s2 = ((words[i*3+1] & 0x0000000F) << (2*4)) + ((words[i*3] & 0xFF000000) >> (6*4))
            s3 = (words[i*3+1] & 0x0000FFF0) >> (1*4)
            s4 = (words[i*3+1] & 0x0FFF0000) >> (4*4)
            s5 = ((words[i*3+2] & 0x000000FF) << (1*4)) + ((words[i*3+1] & 0xF0000000) >> (7*4))
            s6 = (words[i*3+2] & 0x000FFF00) >> (2*4)
            s7 = (words[i*3+2] & 0xFFF00000) >> (5*4)

            samps += [s0, s1, s2, s3, s4, s5, s6, s7]
        return samps

    def getNextTrigger(self):
        """
        This function returns  the next trigger from the dataFile. It reads the control words into h[0-3], unpacks them,
        and then reads the next event. It returns a RawTrigger object, which includes the fileName, location in the
        file, and a dictionary of the traces
        :raise:IOError if the header does not pass a sanity check: (sanity = 1 if (i0 & 0xa0000000 == 0xa0000000) else 0
        """
        # Instantize a RawTrigger object
        trigger = RawTrigger()
        #print(self.event_counter)
        # Fill the file position
        trigger.filePos = self.file.tell()
        # Read the 4 long-words of the event header
        try:
            i0, i1, i2, i3 = self.get_next_n_words(n_words=4)
        except ValueError:
            return None

        # Check to make sure the event starts with the key value (0xa0000000) and event count is correct, otherwise it's ill-formed
        eventCounterMask = 0x00ffffff
        event_count = i2 & eventCounterMask
        # If not the first file in a run, event counter will not start at 0
        if self.event_counter==0:
            self.event_counter = event_count

        if ((i0 & 0xF0000000 == 0xa0000000) and (abs(event_count - self.event_counter) < 10)):
            trigger.sanity = 0 # normal
        else:
            trigger.sanity = 0 # not good, but let's keep going
            start_pos = self.file.tell()
            if self.verbosity>=1:
                print('Info: Read did not pass sanity check')
                print('Info: Last read headers:')
                print(hex(i0), hex(i1), hex(i2), hex(i3))
                print("Start skipping...1 byte at a time...until the next good header...")
            while (True):
                #print("skipping a byte")
                b = self.get_next_byte()
                current_pos = self.file.tell()
                if current_pos - start_pos > 64016:
                    print("Taking too long to find next event")
                    print(start_pos)
                    return None
                #print(self.file.tell())
                if b is None:
                    return None
                #print(hex(b))
                if (b & 0xF0 == 0xa0):
                    #print("Stop")
                    #break
                    #print(self.file.tell())
                    i0, i1, i2, i3 = self.get_next_n_words(n_words=4, byte_offset=-4)
                    #print(self.file.tell())
                    eventCounterMask = 0x00ffffff
                    event_count = i2 & eventCounterMask
                    #print(event_count)
                    if (abs(event_count - self.event_counter) < 10):
                        #print(self.file.tell())
                        #print(event_count)
                        break
                    self.file.seek(-12, 1)

        # extract the event size from the first header long-word
        eventSize = i0 - 0xa0000000

        # extract the board ID and channel map from the second header long-word
        boardId = (i1 & 0xf8000000) >> 27
        trigger.boardId = boardId #Xin
        if boardId > 3:
            print("Board ID too high")
            print(trigger.filePos)
        if boardId == 3:
            trigger.brdtype = "V1740"
        else:
            trigger.brdtype = "V1730"

        if trigger.brdtype == "V1730":
            # For 16ch boards, the channelMask is split over two header words, ref: Tab. 8.2 in V1730 manual
            # To get the second half of the channelMask to line up properly with the first, we only shift it by
            # 16bits instead of 24.
            channelUse = (i1 & 0x000000ff) + ((i2 & 0xff000000) >> 16)

            # convert channel map into an array of 0's or 1's indicating which channels are in use
            whichChan = [1 if (channelUse & 1 << k) else 0 for k in range(16)]

            # determine the number of channels that are in the event by summing whichChan
            numChannels = int(sum(whichChan))

            if numChannels<=0:
                return None

        elif trigger.brdtype == "V1740":
            # For V1740, there are 8 groups of 8 channels each. If a group is enabled, all channels in that group are enabled
            # The groupMask is only in the second header word.
            groupMask = i1 & 0x000000ff

            # convert group map into array of 1s and 0s indicating which groups are enabled
            whichGroups = [1 if (groupMask & 1 << k) else 0 for k in range(8)]

            # determine the number of groups that are enabled by summing whichGroups
            numGroups = int(sum(whichGroups))

            if numGroups<=0:
                return None

        # Test for zero-length encoding by looking at one bit in the second header long-word
        # Is this being used????
        zLE = True if i1 & 0x01000000 != 0 else False

        # Create an event counter mask and then extract the counter value from the third header long-word
        eventCounterMask = 0x00ffffff
        trigger.eventCounter = i2 & eventCounterMask
        self.event_counter = trigger.eventCounter

        # The trigger time-tag (timestamp) is the 31-bit of 4th world
        pattern_bits = (i1 >> 8) & 0xffff
        rollover_bit = i3 >> 31
        if self.ETTT_flag:
            ttt = pattern_bits * 2**32 + i3
        else:
            rollover_bit = i3 >> 31
            if rollover_bit == 1: # rollover already occured
                ttt = i3 & 0x7FFFFFFF
            else:
                ttt = i3

        # Since the trigger time tag may rolls over
        if ttt < self.oldTimeTag[boardId]:
            self.timeTagRollover[boardId] += 1
            self.oldTimeTag[boardId] = uint64(ttt)
            # print('Trigger Time Rollover')
        else:
            self.oldTimeTag[boardId] = uint64(ttt)

        # correcting triggerTimeTag for rollover
        if self.ETTT_flag:
            trigger.triggerTimeTag =  ttt + self.timeTagRollover[boardId]*(2**48)
        else:
            trigger.triggerTimeTag = ttt + self.timeTagRollover[boardId]*(2**31)

        # convert from ticks to us since the beginning of the file
        trigger.triggerTime = trigger.triggerTimeTag * 8e-3

        # Calculate length of each trace, using eventSize (in long words) and removing the 4 long words from the header
        size = int(4 * eventSize - 16) # Event size in bytes minus the header

        if trigger.brdtype == "V1730":
            self.recordLen = size//(2*numChannels) # Xin: save the length of traces

            # looping over the entries in the whichChan list, only reading data if the entry is 1
            for ind, k in enumerate(whichChan):
                if k == 1:
                    # create a name for each channel according to the board and channel numbers
                    traceName = "b" + str(boardId) + "_ch" + str(ind)

                    # If the data are not zero-length encoded (default)
                    if not zLE:
                        # create a data-type of unsigned 16bit integers with the correct ordering
                        if self.DAQ_Software=='LabVIEW':
                            dt = dtype('>H')
                        else:
                            dt = dtype('<H') # Xin: LabVIEW and ToolDAQ have different ordering

                        # Use numpy's fromfile to read binary data and convert into a numpy array all at once
                        trace = fromfile(self.file, dtype=dt, count=size//(2*numChannels))

                        # sanity check again (the left two bits should be empty)
                        l2 = np.right_shift(trace, 14)
                        if np.any(l2 > 0):
                            trigger.sanity = 1

                    else:
                        # initialize an array of length self.recordLen, then set all values to nan
                        trace = zeros(self.recordLen)
                        trace[:] = nan

                        # The ZLE encoding uses a keyword to indicate if data to follow, otherwise number of samples to skip
                        (trSize,) = fromfile(self.file, dtype='I', count=1)

                        # create two counting indices, m and trInd, for keeping track of our position in the trace and
                        m = 1
                        trInd = 0

                        # create a data-type for reading the binary data
                        dt = dtype('<H')

                        # loop while the m counter is less than the total size of the trace
                        while m < trSize:
                            # extract the control word from the data
                            (controlWord,) = fromfile(self.file, dtype='I', count=1)

                            # determine the number of bytes to read, and convert into samples (x2)
                            length = (controlWord & 0x001FFFFF) * 2

                            # determine whether that which follows are data or number of samples to skip
                            good = controlWord & 0x80000000

                            # If they are data...
                            if good:

                                # Read and convert the data (length is
                                tmp = fromfile(self.file, dtype=dt, count=length)
                                # insert the read data into the empty trace otherwise full of NaNs
                                trace[trInd:trInd + length] = tmp

                            # Increment both the trInd and m indexes by their appropriate amounts
                            trInd += length
                            m += 1 + (length/2 if good else 0)

                    # create a dictionary entry for the trace using traceName as the key
                    trigger.traces[traceName] = trace

            self.trigger_counter += 1
            return trigger

        elif trigger.brdtype == "V1740":
            # 1.5 bytes per sample, 8 channels per group
            self.recordLen = size//(12*numGroups)

            # Looping over the entries in whichGroups, only reading data if entry is 1
            for ind, k in enumerate(whichGroups):
                if k == 1:
                    # Looping over all 8 channels in group
                    for chan in range(8):
                        # Create a name for each channel according to board, group, and channel
                        traceName = "b" + str(boardId) + "_ch" + str(ind*8 + chan)
                        trigger.traces[traceName] = []

                    # If not zero length encoded
                    if not zLE:
                        # Create a 32-bit datatype with correct endianness
                        dt = dtype('<u4')

                        # Loop over all samples in group
                        for j in range(self.recordLen//3):
                            # Read 9 words
                            words = self.get_next_n_words(n_words=9)

                            # Decode 24 samples
                            samps = self.decode_V1740_data(words)

                            # Add samples to trace
                            for k in range(len(samps)//3):
                                name = "b" + str(boardId) + "_ch" + str(ind*8 + k)
                                trigger.traces[name] += samps[3*k:3*k+3]

                    else:
                        print("Error! Zero-Length Encoding not implemented for V1740")

            self.trigger_counter += 1
            return trigger

    def close(self):
        """
        Close the open data file. Helpful when doing on-the-fly testing
        """
        self.file.close()


# =============================================
# ============ Raw Trigger Class ==============
# =============================================


class RawTrigger:
    def __init__(self):
        """
        This is a class to contain a raw trigger from the .dat file. This is before any processing is done. It will
        contain a dictionary of the raw traces, as well as the fileName of the .dat file and the location of this
        trigger in the raw data.
        """
        self.traces = {}
        self.filePos = 0
        self.triggerTimeTag = uint64(0)
        self.triggerTime = 0.
        self.eventCounter = 0
        self.sanity = 0
        self.brdtype = "V1730"

        #Xin added
        self.boardId = 0
        self.size = 0

    def display(self, trName=None):

        """
        A method to display any or all the traces in the RawTrigger object
        :param trName: string or list, name of trace to be displayed
        """

        fig = plt.figure(figsize=[11,5])
        ax = fig.add_subplot(111)

        if trName is None:
            for trace in sorted(self.traces.items()):
                plt.plot(trace[1], label=trace[0])
        else:
            if isinstance(trName, str):
                plt.plot(self.traces[trName], label=trName)
            elif isinstance(trName, list):
                for t in trName:
                    plt.plot(self.traces[t], label=t)
        ax.legend(loc=0)

        # place a text box in upper left in axes coords with details of event
        textstr = 'File Position: {}\nTrigger Time (us): {}\nEvent Counter: {}'\
            .format(self.filePos, self.triggerTime, self.eventCounter)

        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7))

        ymin, ymax = plt.ylim()

        plt.ylim(ymax=ymax + (ymax-ymin)*.15)

        plt.xlabel('Samples')
        plt.ylabel('ADU')
        plt.grid()
        plt.show()

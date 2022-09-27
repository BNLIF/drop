"""
Utility functions that are used by DROP
"""
import math
import numpy as np
from scipy import signal
from matplotlib.colors import ListedColormap
from matplotlib.cm import hsv
from yaml_reader import SAMPLE_TO_NS


def generate_colormap(n_colors=32):
    """
    This function is copied from:
    https://stackoverflow.com/questions/42697933/colormap-with-maximum-distinguishable-colours
    For best visibility, set n_colors = number of channels
    """
    n_shades = 7
    n_fades = int(math.ceil(n_colors / n_shades) * n_shades)

    linear_nums = np.arange(n_fades) / n_fades
    arr_by_shade_rows = linear_nums.reshape(n_shades, n_fades // n_shades)

    arr_by_shade_columns = arr_by_shade_rows.T
    n_partitions = arr_by_shade_columns.shape[0]
    nums_distributed_like_rising_saw = arr_by_shade_columns.reshape(-1)
    initial_cm = hsv(nums_distributed_like_rising_saw)


    lower_partitions = n_partitions // 2
    upper_partitions = n_partitions - lower_partitions

    lower_half = lower_partitions * n_shades
    for i in range(3):
        initial_cm[0:lower_half, i] *= np.arange(0.2, 1, 0.8/lower_half)

    for i in range(3):
        for j in range(upper_partitions):
            modifier = np.ones(n_shades) - initial_cm[lower_half + j * n_shades: lower_half + (j + 1) * n_shades, i]
            modifier = j * modifier / upper_partitions
            initial_cm[lower_half + j * n_shades: lower_half + (j + 1) * n_shades, i] += modifier

    return ListedColormap(initial_cm)



def digitial_butter_highpass_filter(data, cutoff_Hz=3e6):
    """
    data: 1d ndarray
    cutoff_Hz: cut off digitizer sampling freq in hz
    Source: https://scipy-cookbook.readthedocs.io/items/ButterworthBandpass.html
    """
    order=5
    fs_Hz = 1e9/SAMPLE_TO_NS # digitizer sampling rate
    nyq = fs_Hz * 0.5
    Wn = cutoff_Hz/nyq
    b, a = signal.butter(order, Wn, btype='high', analog=False)
    return signal.filtfilt(b, a, data)

def linear_interpolation(x_arr, y_arr, y, rising_edge=True):
    """
    Linear interpolation
    Given fy, fx, and y, find x.
    If multiple solution exist, return the first one.
    rising_edge bool can be used to select rising slope or falling slope

    Note:
        this is similar but not identical to np.interp.
    """
    x_l = x_arr[:-1]; x_h = x_arr[1:]
    y_l = y_arr[:-1]; y_h = y_arr[1:]
    if rising_edge:
        mask= (y_l<=y) & (y<y_h)
    else:
        mask= ((y<=y_l) & (y>y_h))
    i = np.where(mask)[0][0]
    print(y, x_l[i], (x_h[i]-x_l[i]), (y_h[i]-y_l[i])*(y-y_l[i]))
    return x_l[i]+(x_h[i]-x_l[i])/(y_h[i]-y_l[i])*(y-y_l[i])

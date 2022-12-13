"""
A set of numba compatiable functions goes here
Create a library of pre-compile numba function for the accelerated performance
Must compile before using the functions.

Reference:
https://numba.readthedocs.io/en/stable/user/pycc.html
"""

from numba.pycc import CC
import numpy as np
import os
LIB_DIR = os.environ['LIB_DIR']

cc = CC('utilities_numba')
cc.output_dir=LIB_DIR
# Uncomment the following line to print out the compilation steps
#cc.verbose = True

@cc.export('quantile_f8', 'f8[:](f8[:], f8[:])')
@cc.export('quantile_u2', 'f8[:](u2[:], f8[:])')
def quantile(a, q):
    """
    Accelerated np.quantile function

    Args:
    a: 1d numpy array
    q: 1d numpy array
    """
    qx = np.quantile(a, q)
    return qx

@cc.export('std', 'f8(f8[:])')
def std(a):
    """
    Accelerated np.std function
    """
    return np.std(a)

@cc.export('max', 'f8(f8[:])')
def max(a):
    return np.max(a)

@cc.export('min', 'f8(f8[:])')
def min(a):
    return np.min(a)

@cc.export('linear_interpolation', 'f8(f8[:], f8[:], f8, b1)')
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
    return x_l[i]+(x_h[i]-x_l[i])/(y_h[i]-y_l[i])*(y-y_l[i])

@cc.export('aft', 'f8(f8[:], f8[:], f8)')
def aft(t, a_int, y):
    """
    Get Area Fraction Time (AFT) at y*100 pct.
    t, and a_int must have the same dimension

    After the first three lines, it's the same as linear_interpolation
    """
    if a_int[-1]==a_int[0]:
        return t[0]
    else:
        x_arr = t
        y_arr = (a_int-a_int[0])/(a_int[-1]-a_int[0])
        x_l = x_arr[:-1]; x_h = x_arr[1:]
        y_l = y_arr[:-1]; y_h = y_arr[1:]
        mask= (y_l<=y) & (y<y_h)
        i = np.where(mask)[0][0]
        return x_l[i]+(x_h[i]-x_l[i])/(y_h[i]-y_l[i])*(y-y_l[i])

@cc.export('rise_time', 'f8(f8[:], f8[:], f8)')
def rise_time(x_arr, y_arr, spe_thresh=0.125):
    """
    Get rise time (10% to 90% height).
    Similar to linear_interpolation only rising edge.

    Args:
        x_arr: this is time axis. Array.
        y_arr: this is baseline subtracted waveform (baseline must be at ~0). Array.
        spe_thresh: SPE threshold. float
    """
    # if peak is below thresold to be considered a SPE
    ymax = np.max(y_arr)
    if ymax<spe_thresh:
        return -1
    # if peak is the first element
    imax = np.argmax(y_arr)
    if imax==0:
        return 0
    y10 = ymax*0.1 # 10% of max height
    y90 = ymax*0.9 # 90% of max height
    x_l = x_arr[:-1]; x_h = x_arr[1:]
    y_l = y_arr[:-1]; y_h = y_arr[1:]
    msk10 = np.where((y_l<=y10) & (y10<y_h))[0]
    msk90 = np.where((y_l<=y90) & (y90<y_h))[0]
    if msk10.size==0 or msk90.size==0:
        return -2
    i = msk10[0]; t10 = x_l[i]+(x_h[i]-x_l[i])/(y_h[i]-y_l[i])*(y10-y_l[i])
    i = msk90[0]; t90 = x_l[i]+(x_h[i]-x_l[i])/(y_h[i]-y_l[i])*(y90-y_l[i])
    return t90-t10

if __name__ == "__main__":
    cc.compile()

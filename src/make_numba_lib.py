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

if __name__ == "__main__":
    cc.compile()

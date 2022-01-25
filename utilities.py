import math

import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.cm import hsv

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

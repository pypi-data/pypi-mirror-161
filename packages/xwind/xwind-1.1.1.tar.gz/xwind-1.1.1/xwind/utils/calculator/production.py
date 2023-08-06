import numpy as np
import pandas as pd
import scipy.interpolate.interpolate as ip


def single_calc_prod_by_freq_powercurve(freq: pd.Series, power_curve: pd.Series) -> float:
    """单风频单功率曲线计算

    Args:
        freq (pd.Series): [description]
        power_curve (pd.Series): [description]

    Returns:
        float: [description]
    """
    index = power_curve.index
    d1 = ip.interp1d(freq.index, freq.values, kind='cubic')
    freq_needed = d1(index)
    return np.sum(freq_needed * power_curve.values)

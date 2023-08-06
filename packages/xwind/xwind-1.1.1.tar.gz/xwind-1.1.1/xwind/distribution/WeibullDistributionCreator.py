# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 15:08:16 2018

@author: hu578
"""
import math
from typing import Tuple

import numpy as np
import pandas as pd
from scipy import stats


class WblDistribution:
    def __init__(self, scale: float, shape: float, speed: float = 0):
        self.scale = scale
        self.shape = shape
        self.speed = speed
        if speed != 0:
            self.scale = get_ak(speed, shape)[0]
        self.wbl = stats.weibull_min(self.shape, 0, self.scale)

    def create_custom_flag(self, custom_flag_left: np.ndarray, custom_flag_right: np.ndarray):
        middle_flag = (custom_flag_right + custom_flag_left) / 2
        fre = self.wbl.cdf(custom_flag_right) - self.wbl.cdf(custom_flag_left)
        return pd.DataFrame(
            {"风速区间中值": middle_flag, "左边界": custom_flag_left, "右边界": custom_flag_right, "风频": fre})

    def create(self, method: int = 2):
        """可选四种创建模式创建风频

        :param method: 共4种选择(0,1,2,3)，默认为2
                method=0: 上限法，以 0.5m/s 为间隔，[2.5-3] [3-3.5] [3.5-4]
                method=1: 上限法，以 1m/s 为间隔， [2-3] [3-4] [4-5]
                method=2: 中值法，以 0.5m/s 为间隔， [2.25-2.75][2.75-3.25][3.25-3.75]
                method=3: 中值法，以 1m/s 为间隔， [2.5-3.5] [3.5-4.5] [4.5-5.5]
        :return: 带有左边界、有边界、风频的DataFrame
        """
        if method == 0:
            left = np.arange(2, 30.1, 0.5)
            right = left + 0.5
            fre = self.wbl.cdf(right) - self.wbl.cdf(left)
            return pd.DataFrame({"风速区间中值": left + 0.25, "左边界": left, "右边界": right, "风频": fre})
        if method == 1:
            left = np.arange(2, 30, 1)
            right = left + 1
            fre = self.wbl.cdf(right) - self.wbl.cdf(left)
            return pd.DataFrame({"风速区间中值": left + 0.5, "左边界": left, "右边界": right, "风频": fre})
        if method == 2:
            left = np.arange(2.5, 30.1, 0.5) - 0.25
            right = left + 0.5
            fre = self.wbl.cdf(right) - self.wbl.cdf(left)
            return pd.DataFrame({"风速区间中值": left + 0.25, "左边界": left, "右边界": right, "风频": fre})
        if method == 3:
            left = np.arange(2, 30, 1) - 0.5
            right = left + 1
            fre = self.wbl.cdf(right) - self.wbl.cdf(left)
            return pd.DataFrame({"风速区间中值": left + 0.5, "左边界": left, "右边界": right, "风频": fre})


# @numba.jit
def get_ak(ws: float, k: float) -> Tuple[float, float]:
    return ws / math.gamma(1 + 1 / k), k


# @numba.jit
def get_flag(start, stop, step):
    return np.arange(start, stop + step, step)


def get_dist(flag, scale, shape):
    """
    flag: 风速标识
    scale: 尺度因子
    shape: 形状因子，一般而言是k
    """
    step = flag[2] - flag[1]
    left = flag - step / 2
    right = flag + step / 2
    wbl = stats.weibull_min(shape, 0, scale)
    fre = wbl.cdf(right) - wbl.cdf(left)
    return fre


def get_dist_with_bound_limit(flag, scale, shape) -> np.ndarray:
    """
    有左右边界限制的威布尔参数
    Parameters
    ----------
    flag
    scale
    shape

    Returns
    -------
    一个数组
    """
    step = flag[2] - flag[1]
    left = flag - step / 2
    right = flag + step / 2
    left[0] = flag[0]
    right[-1] = flag[-1]
    wbl = stats.weibull_min(shape, 0, scale)
    fre = wbl.cdf(right) - wbl.cdf(left)
    return fre

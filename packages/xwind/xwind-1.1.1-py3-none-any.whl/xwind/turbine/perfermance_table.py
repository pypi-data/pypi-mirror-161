# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 23:16:12 2019

@author: hu578
"""

import numpy as np
import pandas as pd


class PerformanceTable(object):
    def __init__(
            self,
            air_density: np.ndarray,
            speed_tick: np.ndarray,
            power_curves: np.ndarray,
            ct_curves: np.ndarray
    ):

        (l1, l2, l3, l4) = (
            air_density.shape[0],
            speed_tick.shape[0],
            power_curves.shape,
            ct_curves.shape)
        if (l1 == l3[1] == l4[1]) and (l2 == l3[0] == l4[0]):
            self.power_table = pd.DataFrame(
                data=power_curves,
                index=speed_tick,
                columns=air_density)
            self.ct_table = pd.DataFrame(
                data=ct_curves,
                index=speed_tick,
                columns=air_density)
        else:
            raise Exception("输入参数有误")

    def get_power_curve(self, air_density: float):
        """
        获取固定空气密度下的曲线

        """
        sr = self.power_table[air_density]
        return sr.index.get_values(), sr.values

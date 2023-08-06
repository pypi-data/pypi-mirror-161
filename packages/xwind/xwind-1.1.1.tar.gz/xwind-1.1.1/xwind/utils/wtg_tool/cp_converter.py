# -*- coding: utf-8 -*-
"""
Created on Thu May  3 17:07:13 2018
功率曲线的cp计算
@author: huqin
"""
import math

import numpy as np
import pandas as pd


def series_cp(curve: pd.Series, radius: float) -> pd.Series:
    """计算一个功率曲线序列的cp系数

    Args:
        curve (pd.Series): 功率曲线序列Series，以风速为行的index，以空气密度为name
        radius (float): 半径

    Returns:
        pd.Series: cp序列Series
    """
    density = curve.name
    area = math.pi * radius ** 2
    theory_power = 0.5 * density * area * np.power(curve.index, 3) / 1000
    cp_sr = curve / theory_power
    cp_sr.name = density  # series运算完无法重现name属性
    return cp_sr


def dataframe_cp(df: pd.DataFrame, radius: float) -> pd.DataFrame:
    """计算一个功率曲线集的cp系数，df是以空气密度为列标题，风速为行index的dataframe

    Args:
        df (pd.DataFrame): 功率曲线dataframe
        radius (float): 机组半径

    Returns:
        pd.DataFrame: cp系数dataframe
    """
    row, col = df.shape
    density = df.columns.values.reshape(1, col)  # 一行多列，为了实现numpy数组广播，(r,1)*(1,c)=(r,c)
    area = math.pi * radius ** 2
    speed = df.index.values.reshape(row, 1)  # 一列多行，为了实现numpy数组广播，(r,1)*(1,c)=(r,c)
    theory_power = 0.5 * density * area * np.power(speed, 3) / 1000
    return df / theory_power

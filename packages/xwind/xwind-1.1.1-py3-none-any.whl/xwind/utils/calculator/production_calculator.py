# -*- coding: utf-8 -*-
"""
Created on Thu May  3 19:13:48 2018

@author: hu578
"""
import numpy as np


def calculate_production(freq: np.array, curves: np.array):
    """
    本函数已经假定你的风频和功率曲线是对齐的，并提供发电量矩阵
    :param freq:风频
    :param curves:功率曲线矩阵(包含多列功率曲线)
    :return:发电量矩阵，并在矩阵的最后一行添加求和结果
    """
    freq = np.asarray(freq, np.float)
    curves = np.asarray(curves, np.float)
    r, c = curves.size
    freq = freq.reshape([r, 1])
    prods = freq * curves
    prod = np.sum(prods, axis=0)
    return np.row_stack((prods, prod))

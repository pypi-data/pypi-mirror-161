# import numba
from typing import Callable

import numpy as np
# from numba import float32, float64, vectorize
from scipy import interpolate


def Lagerange(x: float,
              x1: float, y1: float,
              x2: float, y2: float,
              x3: float, y3: float,
              x4: float, y4: float) -> float:
    """[拉格朗日插值]

    Args:
        x (float): 待插值坐标
        x1 (float):
        y1 (float):
        x2 (float):
        y2 (float):
        x3 (float):
        y3 (float):
        x4 (float):
        y4 (float):

    Returns:
        float: x处的y值
    """
    a1 = (x - x2) * (x - x3) * (x - x4) / (x1 - x2) / (x1 - x3) / (x1 - x4)
    a2 = (x - x1) * (x - x3) * (x - x4) / (x2 - x1) / (x2 - x3) / (x2 - x4)
    a3 = (x - x1) * (x - x2) * (x - x4) / (x3 - x1) / (x3 - x2) / (x3 - x4)
    a4 = (x - x1) * (x - x2) * (x - x3) / (x4 - x1) / (x4 - x2) / (x4 - x3)
    y = a1 * y1 + a2 * y2 + a3 * y3 + a4 * y4
    return y


def lagrange_func(x: np.ndarray, y: np.ndarray) -> Callable[[float], float]:
    """Return lagrange function
    :param x: 横坐标x值
    :param y: 纵坐标y值
    :return 返回一个function，后续使用f(x)得到结果
    """

    a0 = x[[1, 2, 3]]
    a1 = x[[0, 2, 3]]
    a2 = x[[0, 1, 3]]
    a3 = x[[0, 1, 2]]
    aa0 = x[0] - a0
    aa1 = x[1] - a1
    aa2 = x[2] - a2
    aa3 = x[3] - a3

    def lar_func(xnew):
        aaa0 = np.prod(xnew - a0) / np.prod(aa0)
        aaa1 = np.prod(xnew - a1) / np.prod(aa1)
        aaa2 = np.prod(xnew - a2) / np.prod(aa2)
        aaa3 = np.prod(xnew - a3) / np.prod(aa3)
        return np.array(np.sum([aaa0, aaa1, aaa2, aaa3] * y))

    return lar_func


def LinearExtroplation(x, x1, y1, x2, y2):
    k = (y2 - y1) / (x2 - x1)
    y = k * (x - x1) + y1
    return y


def linear_interpolation(x: np.ndarray,
                         y: np.ndarray,
                         new_x: np.ndarray) -> np.ndarray:
    """
    x和y的长度必须一致
    """
    f = interpolate.interp1d(x, y)
    new_y = f(new_x)
    return new_y


# @vectorize([float64(float64)])
def transform_speed_exponents(speed):
    """风速转化时的指数因子.
    This improved method is (will be, as of writing) published
    and presented at the EWEC 2010 conference
    (Author: Lasse Svenningsen, Title: Proposal of an improved power curve air-density correction).
    Parameters
    ----------
    speed:float64:

    Returns
    -------
    factor:float64:风转化因子
    """
    line_x = [0, 7.5, 12.5, 50]
    line_y = [1 / 3, 1 / 3, 2 / 3, 2 / 3]
    return np.interp(speed, line_x, line_y)

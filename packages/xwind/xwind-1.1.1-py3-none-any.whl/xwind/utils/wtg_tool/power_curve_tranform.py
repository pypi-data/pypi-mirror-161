"""本模块用于功率曲线转换，含有IEC方法和实际客观法！
作者的个人理解中，如果测试功率曲线环境是低空气密度，则IEC方法较好；
如果测试功率曲线环境是标空，那么对低空气密度的转换应该用improved方法，该方法得到的功率曲线更低更客观。
根据性能检查原理，所有的功率曲线达标检测都是转换至标空的，因此IEC方法在这方面是可行的，但是IEC方法换算得到的较低空气密度功率曲线会偏高，会高估电量。
"""
from typing import List

import pandas as pd
from scipy.interpolate import pchip

from ...general_functions.interpolate import *


def target_speed_in_ref_density(target_speed, target_density, ref_density):
    """
    ref是已知的空气密度和功率曲线风速，target是要转换的目标空气密度和风速。
    ρt*(vt**3)=ρr*(vr**3)
    vr=pow(ρt/ρr,1/3)*vt
    """
    factor = np.power(target_density / ref_density, 1.0 / 3.0)
    return factor * target_speed


def transform_power_curve_arrays_with_improved_method(
        speed: np.ndarray,
        power: np.ndarray,
        density: float,
        new_density: float) -> np.ndarray:
    # 获取风速标识下的指数
    trans_exp = transform_speed_exponents(speed)
    # 新空气密度下的风速，相当于标空风速的转换
    density_factor = new_density / density
    new_speed = speed * np.power(density_factor, trans_exp)
    interp = pchip(speed, power, extrapolate=True)
    new_curve = interp(new_speed)
    new_curve[0] = new_density / density * power[0]
    return new_curve


def transform_power_curve_series_with_improved_method(
        curve: pd.Series,
        new_density: float) -> pd.Series:
    speed = curve.index
    power = curve.values
    density = curve.name
    new_value = transform_power_curve_arrays_with_improved_method(
        speed, power, density, new_density)
    return pd.Series(data=new_value, index=speed, name=new_density)


def transform_power_curve_arrays_with_IEC_method(
        speed: np.ndarray,
        power: np.ndarray,
        density: float,
        new_density: float) -> np.ndarray:
    density_factor = new_density / density
    # 把new_density下的speed转化到density下的等效speed
    new_speed = speed * np.power(density_factor, 1.0 / 3.0)
    # 构建原曲线的插值方程
    interp = pchip(speed, power, extrapolate=True)
    # 从原曲线上获取等效风速刻度上的功率值
    new_curve = interp(new_speed)
    new_curve[0] = new_density / density * power[0]
    return new_curve


def transform_power_curve_series_with_IEC_method(
        curve: pd.Series,
        new_density: float) -> pd.Series:
    """[summary]

    Args:
        curve (pd.Series): [description]
        new_density (float): [description]

    Returns:
        pd.Series: [description]
    """
    speed = curve.index
    power = curve.values
    density = curve.name
    new_value = transform_power_curve_arrays_with_IEC_method(
        speed, power, density, new_density)
    return pd.Series(data=new_value, index=speed, name=new_density)


def transform_curve_from_IEC_to_improved_method(curve: pd.Series) -> pd.Series:
    """将IEC方法转换的功率曲线转到使用优化方法下的功率曲线

    Args:
        curve (pd.Series): [description]

    Returns:
        pd.Series: [description]
    """
    orgin_density = curve.name
    std = transform_power_curve_series_with_IEC_method(curve, 1.225)
    fixed_curve = transform_power_curve_series_with_improved_method(
        std, orgin_density)
    return fixed_curve


def extend_density_with_improved_method(std_curve: pd.DataFrame, densities: List[float],
                                        include_std_curve=True) -> pd.DataFrame:
    """扩展标准功率曲线,使用论文中的方法

    Args:
        std_curve (pd.DataFrame): 功率曲线集，必须包含1.225标空曲线
        densities (list[float]): [description]
        include_std_curve (bool) : 是否包含原有功率曲线

    Returns:
        pd.DataFrame: [description]
    """
    std = std_curve[1.225]
    srs = [transform_power_curve_series_with_improved_method(
        std, den) for den in densities]

    df = pd.concat(srs, axis=1)
    if include_std_curve:
        df[1.225] = std
    return df


def extend_density_with_IEC_method(std_curve: pd.DataFrame, densities: List[float],
                                   include_std_curve=True) -> pd.DataFrame:
    """扩展标准功率曲线,使用IEC中的方法

    Args:
        std_curve (pd.DataFrame): 功率曲线集，必须包含1.225标空曲线
        densities (list[float]): [description]
        include_std_curve (bool) : 是否包含原有功率曲线

    Returns:
        pd.DataFrame: [description]
    """
    std = std_curve[1.225]
    srs = [transform_power_curve_series_with_IEC_method(
        std, den) for den in densities]

    df = pd.concat(srs, axis=1)
    if include_std_curve:
        df[1.225] = std
    return df

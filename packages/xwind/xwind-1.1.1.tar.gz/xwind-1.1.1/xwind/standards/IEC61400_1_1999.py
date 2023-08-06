import numpy as np
import pandas as pd

from . import common


def normal_turbulence_model():
    """
    1999版常规湍流模型,本函数只返回sigma，湍流需要自己计算，或者使用normal_turbulence函数

    根据此公式页的脚注，在计算载荷工况时(load_cases)，除了本公式外，可能还要使用不同的合适的百分位值，这些百分位值可以考虑增加一个值到此公式。
    Δσ1=(x-1)*2*i15,x由百分位值反推,如95%的正态分布为1.64倍标准偏差，那么x取1.64；i15根据IEC A类与IEC B类不同。

    Returns:
    
    返回一个DataFrame,从‘A'索引IEC A，从’B'索引IEC B
    """
    i15_a, i15_b = 0.18, 0.16
    iec_a_factor, iec_b_factor = 2, 3
    v = np.arange(1, 41)
    sigma_a = i15_a * (15 + iec_a_factor * v) / (iec_a_factor + 1)
    sigma_b = i15_b * (15 + iec_b_factor * v) / (iec_b_factor + 1)
    return pd.DataFrame({'A': sigma_a, 'B': sigma_b}, index=v)


NTM = normal_turbulence_model()


def normal_turbulence() -> pd.DataFrame:
    """1999版标准湍流

    Returns:
    
        pd.DataFrame: 返回一个DataFrame,从‘A'索引IEC A，从’B'索引IEC B
    """
    ntm = normal_turbulence_model()
    return ntm.div(ntm.index, axis=0)


def characteristic_turbulence(speed_arr: np.ndarray, std_arr: np.ndarray) -> pd.Series:
    """
    特征湍流的标准偏差计算
    需要注意speed和std的长度是一致的，且是一一对应的。

    Args:
        speed_arr: 风速数组
        std_arr: std数组

    Returns:
    返回一个pd.series,index.values是风速,values是湍流的84%值
    """
    speed_group = common.group_speed_vec(speed_arr)
    df = pd.DataFrame(data={'g': speed_group, 'std': std_arr, 'ti': std_arr / speed_arr})
    grp = df.groupby(by=['g'])
    characteristic_ti: pd.Series = grp['ti'].agg(lambda x: np.percentile(x, 84))
    return characteristic_ti

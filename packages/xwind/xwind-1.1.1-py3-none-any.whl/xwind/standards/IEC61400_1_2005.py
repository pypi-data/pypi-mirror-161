import numpy as np
import pandas as pd

from . import common


def normal_turbulence_model():
    """
    2005版常规湍流模型,90%分位数,本函数只返回sigma，湍流需要自己计算
    根据该版本标准，湍流的对比区间是0.2Vref-0.4Vref之间

    Returns:
    返回一个DataFrame,从‘A'索引IEC A，从’B'索引IEC B,从'C'索引IEC C
    """
    i_ref_a, i_ref_b, i_ref_c = 0.16, 0.14, 0.12
    v = np.arange(1, 31)
    sigma_a = i_ref_a * (0.75 * v + 5.6)
    sigma_b = i_ref_b * (0.75 * v + 5.6)
    sigma_c = i_ref_c * (0.75 * v + 5.6)
    return pd.DataFrame({'A': sigma_a, 'B': sigma_b, 'C': sigma_c}, index=v)


NTM = normal_turbulence_model()


def representative_turbulence(speed_arr: np.ndarray, std_arr: np.ndarray) -> pd.Series:
    """
    代表湍流的标准偏差计算，90%分位数
    需要注意speed和std的长度是一致的，且是一一对应的。

    Args:
        speed_arr: 风速数组
        std_arr: std数组

    Returns:
    返回一个pd.series,index.values是风速,values是湍流的90%值
    """
    speed_group = common.group_speed_vec(speed_arr)
    df = pd.DataFrame(data={'g': speed_group, 'std': std_arr})
    grp = df.groupby(by=['g'])
    representative_std: pd.Series = grp['std'].agg(lambda x: np.percentile(x, 90))
    return representative_std.div(representative_std.index, axis=0)

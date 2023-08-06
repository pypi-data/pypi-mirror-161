"""
本模块包含IEC61400-1-1999，Edition 2的相关公式。该版本的公式主要包含50年一遇，特征湍流
"""

import numpy as np
import pandas as pd


def normal_turbulence_model() -> pd.DataFrame:
    """
    2019版常规湍流模型,本函数只返回sigma，湍流需要自己计算或者使用normal_turbulence函数。
    根据2019版标准，湍流的判断区间为0.6Vr-1.6Vr之间，Vr是额定风速

    Returns:
    返回一个DataFrame,从‘A'索引IEC A，从’B'索引IEC B，从’C'索引IEC C，从’A+'索引IEC A+
    """
    i_ref_a_plus, i_ref_a, i_ref_b, i_ref_c = 0.18, 0.16, 0.14, 0.12
    v = np.arange(1, 31)
    sigma_a_plus = i_ref_a_plus * (0.75 * v + 5.6)
    sigma_a = i_ref_a * (0.75 * v + 5.6)
    sigma_b = i_ref_b * (0.75 * v + 5.6)
    sigma_c = i_ref_c * (0.75 * v + 5.6)
    return pd.DataFrame({'A+': sigma_a_plus, 'A': sigma_a, 'B': sigma_b, 'C': sigma_c}, index=v)


NTM = normal_turbulence_model()


def normal_turbulence() -> pd.DataFrame:
    """标准湍流

    Returns:
        pd.DataFrame: 标准湍流，从‘A'索引IEC A，从’B'索引IEC B，从’C'索引IEC C，从’A+'索引IEC A+
    """
    ntm = normal_turbulence_model()
    return ntm.div(ntm.index, axis=0)

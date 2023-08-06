from pathlib import Path

import numpy as np
import pandas as pd

from .power_curve_tranform import (extend_density_with_IEC_method,
                                   extend_density_with_improved_method)
from .wtg_class import WTG
from .wtg_meta import WTG_META


def extend_and_export_wtg(
    standard_df: pd.DataFrame,
    ct: pd.DataFrame,
    rotor_diameter,
    rated_power,
    cp,
    suggested_heights,
    parent_path,
):
    """扩展空气密度并输出WTG

    Args:
        standard_df (pd.DataFrame): 含有标准空气密度的df
        ct (pd.DataFrame): 含有全部空气密度大ct表
        rotor_diameter ([type]): 直径
        rated_power ([type]): 额定功率
        cp ([type]): cp系数值，不要小数点和百分比
        suggested_heights ([type]): 推荐高度
        parent_path ([type]): 存储文件目录
    """
    wanted_rho = list(np.round(np.arange(0.85, 1.251, 0.01), 2))
    df_full_svenningsen = extend_density_with_improved_method(
        standard_df, wanted_rho, True
    )
    df_full_iec = extend_density_with_IEC_method(standard_df, wanted_rho, True)
    des_iec = f"standard-full-iec-{cp}"
    des_svenningsen = f"standard-full-Svenningsen-{cp}"
    meta_iec = WTG_META(
        RotorDiameter=rotor_diameter,
        Description=des_iec,
        SuggestedHeights=suggested_heights,
    )
    meta_svenningsen = WTG_META(
        RotorDiameter=rotor_diameter,
        Description=des_svenningsen,
        SuggestedHeights=suggested_heights,
    )
    wtg_iec = WTG(df_full_iec, ct, meta_iec)
    wtg_svenningsen = WTG(df_full_svenningsen, ct, meta_svenningsen)
    f = Path(parent_path)
    with f.joinpath(f"XE{rotor_diameter}-{rated_power}-full-iec-{cp}.WTG").open(
        mode="w+t"
    ) as f1:
        wtg_iec.to_wtg_file(f1)
    with f.joinpath(f"XE{rotor_diameter}-{rated_power}-full-Svenningsen-{cp}.WTG").open(
        mode="w+t"
    ) as f2:
        wtg_svenningsen.to_wtg_file(f2)

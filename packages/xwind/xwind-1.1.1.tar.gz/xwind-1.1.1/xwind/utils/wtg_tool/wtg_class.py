import io
from pathlib import Path
from typing import Union

import pandas as pd

from . import parse_wtg
from .cp_converter import dataframe_cp
from .make_wtg import make_wtg_with_DataFrame
from .read_file import read_wt_file
from .wtg_meta import WTG_META


class WTG(WTG_META):
    """wtg类对象
       请注意，除了p-table,t-table,其它所有的属性都应该通过新建一个WTG_META进行赋值。
       可以使用from_wtg函数快速从一个WTG文件中创建类实例
       可以使用from_wt_txt函数快速从WT的文本文件功率曲线中创建类实例
    """

    def __init__(self, power_table: pd.DataFrame, ct_table: pd.DataFrame, meta: WTG_META):
        """[summary]

        Args:
            power_table (pd.DataFrame): 功率特性表
            ct_table (pd.DataFrame): 推力系数特性表
            meta (WTG_META): [description]
        """
        self.power_table = power_table
        self.ct_table = ct_table
        self.__dict__.update(meta.__dict__)

    def set_meta(self, meta: WTG_META):
        """使用meta类可以批量赋值一些属性

        Args:
            meta (WTG_META): wtg中的一些其它信息
        """

        self.__dict__.update(meta.__dict__)

    def get_cp(self) -> pd.DataFrame:
        return dataframe_cp(self.power_table, self.Radius)

    def to_wtg_file(self, file_io: io.StringIO):
        """

        Args:
            file_io: 传入StringIO对象，如果是地址，需要
                with open(path,mode) as f:
                    to_wtg_file(f)
        Returns:

        """
        make_wtg_with_DataFrame(self.power_table,
                                self.ct_table,
                                self.RotorDiameter,
                                self.Description,
                                self.ManufactureName,
                                self.ReferenceURI,
                                self.Comments,
                                self.SuggestedHeights,
                                string_io=file_io)

    def save_as_xlsx(self, file_name: Union[Path, str, io.BytesIO, pd.ExcelWriter]):
        """
        将WTG写入xlsx文件，请注意，不能使用xls作为后缀

        Args:
            file_name: 以xlsx为文件扩展名的路径地址

        Returns:

        """
        with pd.ExcelWriter(file_name) as excel_writer:
            diameter_str = int(self.RotorDiameter)
            self.power_table.to_excel(excel_writer, sheet_name=f'{diameter_str}PowerCurve')
            self.ct_table.to_excel(excel_writer, sheet_name=f'{diameter_str}CtCurve')
            cp = self.get_cp()
            cp.to_excel(excel_writer, sheet_name=f'{diameter_str}Cp')

    @classmethod
    def from_wtg(cls, wtg_file: Union[Path, str]):
        """从WTG文件中读取信息，生成WTG对象

        Args:
            wtg_file: wtg文件路径

        Returns:
            WTG实例对象
        """
        p, t, meta = parse_wtg.parse(wtg_file)
        cl = cls(p, t, meta)
        return cl

    @classmethod
    def from_wt_txt(cls, wt_power_file: Union[Path, str], wt_ct_file: Union[Path, str], density: float):
        """
        从文本文件中读取功率曲线，目前仅匹配WT软件要求的格式

        Args:
            wt_power_file: 功率曲线文件
            wt_ct_file: ct曲线文件
            density: 空气密度

        Returns:
            WTG实例对象

        """
        power_table, ct_table = read_wt_file(wt_power_file, density), read_wt_file(wt_ct_file, density)
        meta = WTG_META()
        meta.RotorDiameter = ct_table.attrs['wt_param'] * 2
        return cls(power_table, ct_table, meta)

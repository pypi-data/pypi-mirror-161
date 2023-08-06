import io
from datetime import datetime
from enum import IntEnum
from functools import cached_property
from io import StringIO

import numpy as np
import pandas as pd


class SectorOptions(IntEnum):
    S4 = 4
    S8 = 8
    S12 = 12
    S16 = 16
    S24 = 24
    S32 = 32
    S36 = 36
    S72 = 72


class TimeData:
    def __init__(
            self,
            data: pd.DataFrame,
            description: str = "",
            sector: SectorOptions = SectorOptions.S16,
            height: int = 100,
    ):
        tempdf = data.dropna()
        upper = tempdf["speed"] < 40
        lower = tempdf["speed"] > 0
        self.data: pd.DataFrame = tempdf[upper & lower]
        self.description = description
        self.sector = sector
        self.height = height

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value: int):
        self._height = value

    @property
    def sector(self):
        return self._sector

    @sector.setter
    def sector(self, value):
        mkey = ("sector_range", "sector_series", "sector_freq")
        for key in mkey:
            if key in self.__dict__.keys():
                del self.__dict__[key]
        self._sector = value

    @cached_property
    def sector_series(self):
        sr = self.data["direction"]
        gap = 360.0 / self.sector
        sr1 = sr.map(lambda x: int((x + gap / 2) % 360 / gap))
        return sr1

    @cached_property
    def sector_range(self):
        return np.arange(0, self.sector)

    @cached_property
    def sector_freq(self) -> pd.Series:
        return self.sector_series.value_counts(normalize=True).sort_index()

    @cached_property
    def bin_series(self):
        sr = self.data["speed"]
        sr1 = sr.apply(lambda x: np.ceil(x).astype('int'))
        sr1.replace(0, 1, inplace=True)  # 不允许出现0值
        return sr1

    @cached_property
    def bin_range(self):
        up = self.bin_series.max()
        if up < 25:
            up = 25
        return np.arange(1, up + 1)

    def get_freq_matrix(self) -> pd.DataFrame:
        tdf = self.data.assign(sector=self.sector_series, bin=self.bin_series)
        groups = tdf.groupby(["sector", "bin"])
        df = groups.agg({"speed": "count"})
        dfr = pd.DataFrame(index=self.bin_range, columns=self.sector_range)
        for ix in df.index:
            sector, s = ix
            dfr.loc[s, sector] = df.loc[ix, "speed"]
        dfr.fillna(0, inplace=True)
        dfr2 = dfr / dfr.sum() * 1000
        dfr2.fillna(0, inplace=True)
        return dfr2.round(2)

    def get_tab_string(self):
        output_io = StringIO()
        output_io.writelines(
            f"{self.description}-created by xwind at {datetime.now()}\n"
        )
        output_io.writelines(f"0.0000 0.0000 {self.height}" + "\n")
        output_io.writelines(f"{self.sector} 1 0\n")
        matrix = self.get_freq_matrix()
        initial_freq = np.zeros(self.sector)
        for ix in self.sector_freq.index:
            freq = np.round(self.sector_freq[ix] * 100, 2)
            initial_freq[ix] = freq
        output_io.writelines('\t'+'\t'.join(initial_freq.astype('str')) + '\n')
        matrix.to_string(output_io, header=False)
        return output_io.getvalue()

    def get_mean_ti_table(self, sample_min=20) -> pd.DataFrame:
        """
            获取ti table，与wt6.5的逻辑基本相同，使用每个时序的ti为计算依据
        Args:
            sample_min: 最小样本数

        Returns:
            pd.DataFrame: mean ti table
        """
        tdf = self.data.assign(sector=self.sector_series, bin=self.bin_series)
        tdf["ti"] = tdf["std"] / tdf["speed"]
        groups = tdf.groupby(["sector", "bin"])
        # 聚合groups运算，得到一个sector和bin的双重索引的dataframe,有ti_mean和count两列
        df2 = groups.agg(ti_mean=("ti", "mean"), count=("speed", "count"))
        # 计算湍流平均值矩阵
        df_avg = pd.DataFrame(index=self.bin_range, columns=self.sector_range)
        for ix in df2.index:
            sector, s = ix
            if df2.loc[ix, "count"] < sample_min:  # 如果样本数小于sample_min,则不计算赋值，调准循环的下一步
                continue
            df_avg.loc[s, sector] = df2.loc[ix, "ti_mean"]
        df_avg.fillna(method="ffill", inplace=True)
        df_avg.fillna(method="bfill", inplace=True)
        df_avg.fillna(0.0, inplace=True)
        return df_avg.round(3)

    def get_mean_ti_string(self, sample_min=20):
        df_avg = self.get_mean_ti_table(sample_min=sample_min)
        sio = io.StringIO()
        sio.write(f'{self.bin_range.max()}\n')
        df_avg.to_string(sio, header=False)
        return sio.getvalue()

    def get_ti_rsd_table(self, sample_min=20) -> pd.DataFrame:
        """获取std的rsd矩阵，与wt6.5的逻辑基本相同，使用每个时序的std为计算依据，风速不参与运算
        Args:
            sample_min: 最小样本数

        Returns:
            std的RSD矩阵
        """
        tdf = self.data.assign(sector=self.sector_series, bin=self.bin_series)
        groups = tdf.groupby(["sector", "bin"])
        agg2 = groups.agg(
            std_mean=("std", "mean"), std_std=("std", "std"), count=("speed", "count")
        )
        df_rsd = pd.DataFrame(index=self.bin_range, columns=self.sector_range)
        for ix in agg2.index:
            sector, s = ix
            if agg2.loc[ix, "count"] < sample_min:  # 如果样本数小于sample_min,则不计算赋值，调准循环的下一步
                continue
            df_rsd.loc[s, sector] = agg2.loc[ix, "std_std"] / agg2.loc[ix, "std_mean"]
        df_rsd.fillna(method="ffill", inplace=True)
        df_rsd.fillna(method="bfill", inplace=True)
        df_rsd.fillna(0.00, inplace=True)
        return df_rsd.round(3)

    def get_ti_rsd_string(self, sample_min=20):
        table = self.get_ti_rsd_table(sample_min)
        sio = io.StringIO()
        sio.write(f"{self.bin_range.max()}\n")
        table.to_string(sio, header=False)
        return sio.getvalue()

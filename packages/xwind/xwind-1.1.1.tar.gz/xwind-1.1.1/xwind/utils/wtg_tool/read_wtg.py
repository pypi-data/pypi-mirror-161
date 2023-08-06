from collections import namedtuple
from typing import Tuple, NewType
from xml.dom import minidom as md

import numpy as np
from deprecated import deprecated

SpeedBins = NewType('SpeedBins', np.ndarray)
Densitys = NewType('Densitys', np.ndarray)
Powercurve = NewType('Powercurve', np.ndarray)
Cts = NewType('Cts', np.ndarray)


@deprecated(reason='应使用parse_wtg替代该函数')
def read_wtg(path) -> Tuple[SpeedBins, Densitys, Powercurve, Cts]:
    """
    :param path:文件路径
    :return :[风速区间矩阵，空气密度矩阵，功率曲线矩阵，推力系数矩阵]
    """
    dom = md.parse(path)
    perf_tables = dom.getElementsByTagName('PerformanceTable')
    columns = perf_tables.length
    parsed_perf_tables = [parse_performance_table(
        perf) for perf in perf_tables]
    perf1 = parsed_perf_tables[0]
    shape = perf1.bins.shape
    rows = shape[0]
    wind_speed_bins = perf1.bins
    density_list = np.zeros(columns)
    powers = np.zeros((rows, columns))
    ct = np.zeros((rows, columns))

    for i in range(columns):
        perf = parsed_perf_tables[i]
        density_list[i] = perf.density
        powers[:, i] = perf.power
        ct[:, i] = perf.ct

    result = namedtuple('WTG', 'wind_speed_bins densitys powers ct')
    rs = result(wind_speed_bins, density_list, powers, ct)
    return rs


def parse_performance_table(pef_table):
    density = float(pef_table.getAttribute('AirDensity'))
    dps = pef_table.getElementsByTagName('DataPoint')
    ld = dps.length
    bins = np.zeros(ld)
    power = np.zeros(ld)
    ct = np.zeros(ld)
    for i in range(dps.length):
        node = dps[i]
        b, p, c = __extract_datapoint(node)
        bins[i] = b
        power[i] = p
        ct[i] = c
    perfType = namedtuple('PerformanceTable', 'density bins power ct')
    return perfType(density, bins, power, ct)


def __extract_datapoint(node) -> Tuple[float, float, float]:
    """

    :param node: DataPoint
    :return: windspeed,power(kW),ct
    """
    b = node.getAttribute('WindSpeed')
    p = node.getAttribute('PowerOutput')
    ct = node.getAttribute('ThrustCoEfficient')
    return float(b), float(p) / 1000, float(ct)

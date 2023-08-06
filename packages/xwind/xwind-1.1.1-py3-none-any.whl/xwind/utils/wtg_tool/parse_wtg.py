import xml.dom.minidom as md
from typing import Tuple

import numpy as np
import pandas as pd

from .wtg_meta import WTG_META


def parse(path: str) -> Tuple[pd.DataFrame, pd.DataFrame, WTG_META]:
    """[解析]

    Args:
        path (str): [wtg路径]

    Returns:
        Tuple[pd.DataFrame,pd.DataFrame,dict]: [power df , ct df , wtg metadata dict]
    """

    dom = md.parse(path)  # 载入文件
    wtg_meta = __get_meta_from_dom(dom)
    # 通过TagName获取所有的表
    ct, power = __get_curve_from_dom(dom)
    return power.fillna(0.0), ct.fillna(0.0), wtg_meta


def __get_meta_from_dom(dom: md.Document) -> WTG_META:
    """获取wtg dom的meta信息：diamter、manufacture、description

    Args:
        dom (md.Document): [description]

    Returns:
        WTG_META: [description]
    """
    root = dom.documentElement
    wtg_meta = WTG_META()
    wtg_meta.RotorDiameter = float(root.getAttribute('RotorDiameter'))
    wtg_meta.ManufactureName = root.getAttribute('ManufacturerName')
    wtg_meta.Description = root.getAttribute('Description')
    wtg_meta.Comments = root.getAttribute('Comments')
    wtg_meta.FormatVersion = root.getAttribute('FormatVersion')
    wtg_meta.ReferenceURI = root.getAttribute('ReferenceURI')
    wtg_meta.ContextInformation = dom.getElementsByTagName('ContextInformation').item(0).nodeValue
    wtg_meta.CertificateChecksum = dom.getElementsByTagName('CertificateChecksum').item(0).nodeValue
    wtg_meta.SuggestedHeights = float(dom.getElementsByTagName('Height').item(0).firstChild.nodeValue)
    return wtg_meta


def parse_wtg_as_df(path: str) -> Tuple[pd.DataFrame, pd.DataFrame, float]:
    """解析wtg文件
    :param path: 文件路径
    :return: (power,ct,height)元组，power,ct为pandas.DataFrame,height为int
    """
    dom = md.parse(path)  # 载入文件
    root = dom.documentElement
    diameter_str = root.getAttribute('RotorDiameter')
    # 通过TagName获取所有的表
    ct, power = __get_curve_from_dom(dom)

    return power.fillna(0.0), ct.fillna(0.0), float(diameter_str)


def __get_curve_from_dom(dom: md.Document):
    """获取wtg中的曲线值，并生成dataframe

    Args:
        dom (md.Document): xml.dom.minidom

    Returns:
        ct,power: ct curve,power curve
    """
    perf_tables = dom.getElementsByTagName('PerformanceTable')
    # 每个表执行一次解析
    parsed_result = [__parse_performance_table(perf) for perf in perf_tables]
    pr_len = len(parsed_result)
    power = parsed_result[0][0]
    ct = parsed_result[0][1]
    if pr_len > 1:
        # 如果不止一个密度下的表，则merge到一起，使用index作为关键字拼接
        for ps in parsed_result[1:]:
            power = power.merge(
                ps[0], how='outer', left_index=True, right_index=True)
            ct = ct.merge(ps[1], how='outer', left_index=True, right_index=True)
    del dom
    return ct, power


def __parse_performance_table(pef_table: md.Node) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """单表解析方法
    :param pef_table:单个表
    :return: 以(power,ct)元组的方式返回单表里的功率曲线与推力系数
    """
    density = float(pef_table.getAttribute('AirDensity'))
    dps = pef_table.getElementsByTagName('DataPoint')
    dp_nb = dps.length
    bins = [0] * dp_nb  # pandas建议index使用collection对象，尽管ndarray也是可行的
    power = np.zeros(dp_nb)
    ct = np.zeros(dp_nb)

    def __extract_data_point(node: md.Node) -> Tuple[float, float, float]:
        """
        :param node: DataPoint
        :return: wind speed,power(kW),ct
        """
        ws_nd = node.getAttribute('WindSpeed')
        power_nd = node.getAttribute('PowerOutput')
        ct_nd = node.getAttribute('ThrustCoEfficient')
        return float(ws_nd), float(power_nd) / 1000, float(ct_nd)

    for i in range(dps.length):
        node_i = dps[i]
        b, p, c = __extract_data_point(node_i)
        bins[i] = b
        power[i] = p
        ct[i] = c
    df_power = pd.DataFrame(data={density: power}, index=bins)
    df_ct = pd.DataFrame(data={density: ct}, index=bins)
    return df_power, df_ct

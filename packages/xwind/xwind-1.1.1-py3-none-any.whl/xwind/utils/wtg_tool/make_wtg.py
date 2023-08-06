import io
import xml.dom.minidom as dm
import xml.etree.ElementTree as et
from typing import List

import numpy as np
import pandas as pd


def make_wtg_with_array(p_matrix: np.ndarray, t_matrix: np.ndarray,
                        real_diameter, description, manufacture, ref_url, comment,
                        suggest_height, file_path=None):
    """
    制作wtg的小程序
    :param p_matrix: 功率矩阵，XEMC通用，第一列是风速，第一行是空气密度
    :param t_matrix: 推力系数矩阵，XEMC通用，第一列是风速，第一行是空气密度
    :param real_diameter: 叶轮的真实直径
    :param description: 机型名称
    :param manufacture: 机组制造商
    :param ref_url: 参考网址
    :param comment: 备注
    :param suggest_height:建议轮毂高度
    :return:
    """
    root = et.Element('WindTurbineGenerator')
    root.set("FormatVersion", '1.01')
    root.set("Description", description)
    root.set('ManufacturerName', manufacture)
    root.set('ReferenceURI', ref_url)
    root.set('RotorDiameter', str(real_diameter))
    cmt = et.SubElement(root, 'Comments')
    cmt.text = comment
    sh = et.SubElement(root, 'SuggestedHeights')
    height = et.SubElement(sh, 'Height')
    height.text = suggest_height
    perfs = __parse_matrix_2_data_point(p_matrix, t_matrix)
    root.extend(perfs)
    context = et.SubElement(root, 'ContextInformation')
    info = et.SubElement(context, 'CertificateChecksum')
    info.text = ''
    mdom = dm.parseString(et.tostring(root, encoding='UTF-8'))
    if file_path is not None:
        with open(f'./wtgs/{name}' + '.wtg', 'w+') as f:
            mdom.writexml(f, addindent=' ', newl='\n', encoding='UTF-8')
    else:
        with open(file_path, 'w+') as f:
            mdom.writexml(f, addindent=' ', newl='\n', encoding='UTF-8')


def __parse_matrix_2_data_point(p_mat, t_mat):
    '''
    将矩阵转换到pertable
    '''
    ws_flag = p_mat[:, 0]
    row, col = p_mat.shape
    density_ls: List[float] = p_mat[0]
    perf_tables = []
    for i in range(1, col):
        d = density_ls[i]
        perf_table = et.Element('PerformanceTable')
        perf_table.set('AirDensity', str(d))
        perf_table.set('MaximumNoiseLevel', '0')
        perf_table.set('BladePitchAngle', '8')
        perf_table.set('DataStatus', 'Unknown')
        perf_table.set('DataSource', '')
        perf_table.set('ReferenceURI', 'NONE')
        perf_table.set('StationaryThrustCoEfficient', str(t_mat[row - 1, i]))
        start_stop_strategy = et.SubElement(perf_table, 'StartStopStrategy')
        cut_in, cutout = str(ws_flag[1]), str(ws_flag[-1])
        start_stop_strategy.set('LowSpeedCutOut', cut_in)
        start_stop_strategy.set('LowSpeedCutIn', cut_in)
        start_stop_strategy.set('HighSpeedCutIn', cutout)
        start_stop_strategy.set('HighSpeedCutOut', cutout)
        cmt = et.SubElement(perf_table, 'Comments')
        cmt.text = ''
        dt = et.SubElement(perf_table, 'DataTable')
        for j in range(1, row):
            dp = et.SubElement(dt, 'DataPoint')
            dp.set('WindSpeed', str(ws_flag[j]))
            power = float(p_mat[j, i])
            dp.set('PowerOutput', format(power * 1000, '0.0f'))
            dp.set('ThrustCoEfficient', format(t_mat[j, i], '0.6f'))
        perf_tables.append(perf_table)
    return perf_tables


def make_wtg_with_DataFrame(power_dataframe: pd.DataFrame, ct_dataframe: pd.DataFrame, rotor_diameter: float,
                            description: str,
                            manufacture: str, ref_url, comment,
                            suggest_height, string_io: io.StringIO):
    """生成wtg，请注意本函数写入的对象是io，字符串要用open()函数打开io

    Args:
        power_dataframe:
        ct_dataframe:
        rotor_diameter:
        description:
        manufacture:
        ref_url:
        comment:
        suggest_height:
        string_io: io，使用路径字符串时要open()为io对象

    Returns:

    """
    root = et.Element('WindTurbineGenerator')
    root.set("FormatVersion", '1.01')
    root.set("Description", description)
    root.set('ManufacturerName', manufacture)
    root.set('ReferenceURI', ref_url)
    root.set('RotorDiameter', str(rotor_diameter))
    cmt = et.SubElement(root, 'Comments')
    cmt.text = str(comment)
    sh = et.SubElement(root, 'SuggestedHeights')
    height = et.SubElement(sh, 'Height')
    height.text = str(suggest_height)
    perfs = __parse_power_ct_dataframe(power_dataframe, ct_dataframe)
    root.extend(perfs)
    context = et.SubElement(root, 'ContextInformation')
    info = et.SubElement(context, 'CertificateChecksum')
    info.text = ''
    mdom = dm.parseString(et.tostring(root, encoding='UTF-8'))
    mdom.writexml(string_io, addindent=' ', newl='\n', encoding='UTF-8')


def __parse_power_ct_dataframe(power_df: pd.DataFrame, ct_df: pd.DataFrame):
    flag = power_df.index.values
    rho_collection = power_df.columns.values
    perf_tables = []
    for rho in rho_collection:
        perf_table = et.Element('PerformanceTable')
        perf_table.set('AirDensity', str(rho))
        perf_table.set('MaximumNoiseLevel', '0')
        perf_table.set('BladePitchAngle', '8')
        perf_table.set('DataStatus', 'Unknown')
        perf_table.set('DataSource', '')
        perf_table.set('ReferenceURI', 'NONE')
        perf_table.set('StationaryThrustCoEfficient', str(ct_df.loc[flag[-1], rho]))
        start_stop_strategy = et.SubElement(perf_table, 'StartStopStrategy')
        cut_in, cutout = str(flag[0]), str(flag[-1])
        start_stop_strategy.set('LowSpeedCutOut', cut_in)
        start_stop_strategy.set('LowSpeedCutIn', cut_in)
        start_stop_strategy.set('HighSpeedCutIn', cutout)
        start_stop_strategy.set('HighSpeedCutOut', cutout)
        cmt = et.SubElement(perf_table, 'Comments')
        cmt.text = ''
        dt = et.SubElement(perf_table, 'DataTable')
        for j, speed in enumerate(flag):
            dp = et.SubElement(dt, 'DataPoint')
            dp.set('WindSpeed', str(speed))
            # 以rho索引某列loc，然后使用iloc取第j个值 
            # 或者直接df.loc[rho].loc[speed]            
            power = float(power_df.loc[speed, rho])
            dp.set('PowerOutput', format(power * 1000, '0.0f'))
            dp.set('ThrustCoEfficient', format(ct_df.loc[speed, rho], '0.6f'))
        perf_tables.append(perf_table)
    return perf_tables


if __name__ == '__main__':
    real_diameter = input("真实直径[m]:")
    # manufacture = input('制造商:')
    manufacture = 'HEWP'
    suggest_height = input("推荐轮毂高度x:")
    name = input("机型命名：")
    # ref_url = input("参考网址:")
    # comment = input("备注信息:")
    ref_url = 'http://www.hewp.com.cn/'
    comment = ''
    if 'cp' in vars() and 'ct' in vars():
        make_wtg_with_array(vars().get('cp'), vars().get('ct'), real_diameter,
                            name, manufacture, ref_url, comment, suggest_height)

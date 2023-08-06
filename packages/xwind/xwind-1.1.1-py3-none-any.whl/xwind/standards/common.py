"""
本模块包含各个标准可能共用的公式
"""
from enum import IntEnum

import numpy as np


class SpeedTick(IntEnum):
    """
    风速区间间隔
    I1: 以0.1m/s为间隔
    I5: 以0.5m/s为间隔
    I10: 以1m/s为间隔
    """
    I1 = 1  # 以0.1m/s为间隔
    I5 = 5  # 以0.5m/s为间隔
    I10 = 10  # 以1m/s为间隔


class SpeedGroupMethod(IntEnum):
    """
    风速区间标志的分类方法

    Average: 以平均值代表区间，5m/s指(4.5,5.5]，常用于中值法，此法得到的风频计算出的风速是相符的 \r\n
    UpperLimit: 以上限值作为区间标志，5m/s指(4.0,5.0],常用于国外，此法得到的风频计算出的风速偏大0.5*SpeedTick \r\n

    """
    Average = 0
    UpperLimit = 1


# @np.vectorize
# def group_speed(speed, tick: SpeedTick = SpeedTick.I10,
#                 speed_group_method: SpeedGroupMethod = SpeedGroupMethod.Average):
#     """
#
#     Args:
#         speed:
#         tick:
#         speed_group_method:
#
#     Returns:
#
#     """
#     rd_speed = np.round(speed, 1)
#     if tick == SpeedTick.I1:
#         return rd_speed
#     elif tick == SpeedTick.I5:
#         if speed_group_method == SpeedGroupMethod.Average:
#             num = np.floor_divide(rd_speed + 0.25, 0.5)
#         else:
#             num = np.floor_divide(rd_speed - 0.01, 0.5) + 1
#         return num * 0.5
#     elif tick == SpeedTick.I10:
#         if speed_group_method == SpeedGroupMethod.Average:
#             num = np.floor_divide(rd_speed + 0.5 - 0.01, 1)
#         else:
#             num = np.floor_divide(rd_speed - 0.01, 1) + 1
#         return num


def group_speed(speed, tick: SpeedTick = SpeedTick.I10,
                speed_group_method: SpeedGroupMethod = SpeedGroupMethod.Average) -> float:
    """风速分类算法,本函数只计算单个数字,如需计算一列数据，请使用group_speed_vec向量化版函数,自行向量化可参照group_speed_vec的编写方法


    Args:
        speed: 风速输入
        tick: 风速间隔,默认间隔是1.0m/s 可以用SpeedTick赋值，也可以用1,5,10赋值，分别代表[0.1,0.5,1.0]
        speed_group_method: 分类方法,默认值是0平均值法,可以用0,1赋值，分别代表平均值法和上限值法，也可以使用SpeedGroupMethod枚举类型赋值

    Returns:

    """
    # rd_speed = np.int(np.round(speed * 10))  # 用int类处理可以避免电脑的浮点数误差，节省内存
    real_tick = tick / 10.0
    factor1 = np.true_divide(real_tick, (speed_group_method - 2) * -1)  # 中值法需要除以2=（0-2）*-1，上限法除以1=(1-2)*-1
    num = np.floor_divide(speed + factor1 - 0.01, real_tick)  # 减去0.01是为了避免边界数字，刚好是风速精度0.1m/s的1/10，8.0是属于8而不是属于9
    return num * real_tick
    # if tick == SpeedTick.I1:
    #     return rd_speed
    # elif tick == SpeedTick.I5:
    #     if speed_group_method == SpeedGroupMethod.Average:
    #
    #         num = np.floor_divide(rd_speed + 0.25, 0.5)
    #     else:
    #         num = np.floor_divide(rd_speed - 0.01, 0.5) + 1
    #     return num * 0.5
    # elif tick == SpeedTick.I10:
    #     if speed_group_method == SpeedGroupMethod.Average:
    #         num = np.floor_divide(rd_speed + 0.5 - 0.01, 1)
    #     else:
    #         num = np.floor_divide(rd_speed - 0.01, 1) + 1
    #     return num


def group_speed_vec(speed: np.ndarray, tick: SpeedTick = SpeedTick.I10,
                    speed_group_method: SpeedGroupMethod = SpeedGroupMethod.Average) -> np.ndarray:
    """风速分类算法,本函数计算可以计算一个数字或者一个数组，但是返回值都是一个ndarray


    Args:
        speed: 风速输入
        tick: 风速间隔,默认间隔是1.0m/s 可以用SpeedTick赋值，也可以用1,5,10赋值，分别代表[0.1,0.5,1.0]
        speed_group_method: 分类方法,默认值是0平均值法,可以用0,1赋值，分别代表平均值法和上限值法，也可以使用SpeedGroupMethod枚举类型赋值

    Returns:
    np.ndarray: 返回数组
    """
    f = np.vectorize(group_speed, excluded=['tick', 'speed_group_method'])
    return f(speed, tick, speed_group_method)

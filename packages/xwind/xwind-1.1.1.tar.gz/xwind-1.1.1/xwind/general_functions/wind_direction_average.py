import numpy as np


def vector_averaging(direction_sets: np.ndarray,
                     speed_sets: np.ndarray = None) -> np.float64:
    """风向矢量平均求解
    算法来源:https://www.scadacore.com/2014/12/19/average-wind-direction-and-wind-speed/
    Parameters
    ----------
    speed_sets:np.ndarray: 风速集合
    direction_sets:np.ndarray: 风向集合

    Returns
    -------
    direction_average
    """
    if speed_sets is None:
        speed_sets = np.ones(direction_sets.shape)
    # 东西向
    ew_vector = np.sin(np.deg2rad(direction_sets)) * speed_sets
    # 南北向
    ns_vector = np.cos(np.deg2rad(direction_sets)) * speed_sets

    double_pi = np.pi * 2.0
    ew_avg = np.average(ew_vector) * -1  # 地理坐标系的x是数学坐标系的-y
    ns_avg = np.average(ns_vector) * -1  # 地理坐标系的y是数学坐标系的-x
    speed_avg = np.sqrt(ew_avg ** 2 + ns_avg ** 2)
    # 补角
    atan2_direction = np.arctan2(ew_avg, ns_avg)  # 旋转坐标系后，x,y跟数学坐标是反的
    direction_deg = np.degrees(atan2_direction)
    if direction_deg > 180:
        return direction_deg - 180
    elif direction_deg < 180:
        return direction_deg + 180

import numpy as np
from scipy.stats import weibull_min


def weibull_dist(k: float, a: float, x: np.ndarray) -> np.ndarray:
    """

    Parameters
    ----------
    k:形状参数，其它相似的名称有shape、c
    a:尺度参数，其它名称有scale
    x:风速序列，生成的风速频率从x[0]开始，到X[-1]结束，意味着切入前和切出后的频率都不会考虑

    Returns
    -------
    ndarray格式的数组，分别与各个x对应
    """
    start, end = x[0], x[-1]
    xi = (x[1:] + x[:-1]) / 2
    left = np.hstack((start, xi))
    right = np.hstack((xi, end))
    return weibull_min.cdf(right, k, 0, a) - weibull_min.cdf(left, k, 0, a)

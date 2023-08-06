from typing import Tuple, NamedTuple, Callable

import numpy as np
from scipy import optimize, stats
from scipy.stats._stats_mstats_common import LinregressResult


class LinearModelResult(NamedTuple):
    params: LinregressResult
    func: Callable[[np.ndarray], np.ndarray]


def linear_model(x: np.ndarray, y: np.ndarray) -> LinearModelResult:
    res = stats.linregress(x, y)
    return LinearModelResult(params=res, func=lambda x1: res.slope * x1 + res.intercept)


def mcp(x0, y0) -> Tuple[float, float]:
    def func(x, a, b):
        return a * x + b

    curve = optimize.curve_fit(func, x0, y0)
    ar, br = curve[0]
    return lambda x1: func(x1, a=ar, b=br)

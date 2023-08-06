import pandas as pd


class Converter:
    def __init__(self, tim_or_timsigma):
        self._df = pd.read_csv(tim_or_timsigma, sep=r'\s+|,|\t', skiprows=1, header=None)

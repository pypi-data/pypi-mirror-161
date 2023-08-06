import pandas as pd


def joint_probability_distribution(x, y):
    data_pre = pd.DataFrame(zip(x, y), columns=['x', 'y'])
    return data_pre

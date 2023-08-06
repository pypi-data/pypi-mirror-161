import pandas as pd


def read_wt_file(path, density) -> pd.DataFrame:
    """读取WT软件格式的功率曲线与推力系数

    Args:
        path ([type]): [文件路径]
        density ([type]): [空气密度]
    Returns:
        pd.DataFrame: [功率df | ct_df]]
    """
    file = open(path, mode='rb')
    param = file.readline().strip()
    df = pd.read_csv(file, sep='\t', names=[density], index_col=0, skiprows=1)
    df.attrs['wt_param'] = float(param)
    file.close()
    return df

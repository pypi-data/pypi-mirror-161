import pandas as pd


def parse(file: str):
    pd_file = pd.ExcelFile(file)
    dfs = pd.read_excel(pd_file, sheet_name=None)  # set sheet_name=None 读入全部sheet
    sheets = list(dfs.keys())
    fir_df: pd.DataFrame = dfs[sheets[0]]
    fir_row: pd.core.series.Series = fir_df.iloc[:, 0] == '风力发电机'
    fr = fir_row.idxmax()
    for k, v in dfs.items():
        df: pd.DataFrame = v
        df.columns = df.loc[fr]
        df = df.loc[fr + 1:]
        df.set_index('标签', inplace=True)
        df.风力发电机.replace(['X', ' '], ['风机位', '测风塔'], inplace=True)

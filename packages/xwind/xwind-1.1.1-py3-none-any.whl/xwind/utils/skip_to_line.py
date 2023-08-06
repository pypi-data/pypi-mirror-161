import os

import pandas as pd


def skip_to_line(file, line_start, **kwargs):
    if os.stat(file).st_size == 0:
        raise ValueError('Empty File')
    with open(file, encoding='utf-8') as f:
        pos = 0
        while not (cur_line := f.readline()).startswith(line_start):
            pos = f.tell()
        f.seek(pos)
        return pd.read_csv(f, **kwargs)


def find_skip_lines(file, line_start):
    if os.stat(file).st_size == 0:
        raise ValueError("File is empty")
        with open(file, encoding='utf-8') as f:
            lines = 0
            while not (cur_line := f.readline()).startswith(line_start):
                lines = lines + 1
            return lines

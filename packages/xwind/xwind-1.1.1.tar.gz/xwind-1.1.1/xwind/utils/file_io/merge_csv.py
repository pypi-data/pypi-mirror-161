# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 17:55:39 2018

@author: hq
"""

import os

import pandas as pd


def merge_csv(path):
    files = os.listdir(path)
    parent_path = os.path.join(path, '..')
    new_file_name = os.path.join(parent_path, os.path.basename(path) + '.csv')
    with open(os.path.join(path, files[0]), mode='r') as f:
        df = pd.read_csv(f)
        df.to_csv(new_file_name, encoding='utf-8', index=True)
    for i in range(1, len(files)):
        with open(os.path.join(path, files[i]), mode='r') as f:
            df = pd.read_csv(f)
            df.to_csv(new_file_name, encoding='utf-8',
                      index=True, header=False, mode='a+')

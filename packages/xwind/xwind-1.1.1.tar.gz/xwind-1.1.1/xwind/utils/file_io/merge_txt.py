# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 18:03:54 2018

@author: hq
"""

import os


def merge_txt(path):
    files = os.listdir(path)
    path_header = path + '\\'
    with open(path_header + 'merged_result.txt', 'w') as f:
        with open(path_header + files[0], 'r') as f0:
            lines = f0.readlines()
            f.writelines(lines)
        for i in range(1, len(files)):
            with open(path_header + files[i], 'r') as fi:
                lines = fi.readlines()
                f.writelines(lines[1:])

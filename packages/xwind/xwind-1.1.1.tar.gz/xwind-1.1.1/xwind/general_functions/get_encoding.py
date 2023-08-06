# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 16:53:43 2018

@author: hu578
"""
import chardet as cd


def from_string(content):
    length = len(content)
    length = length if length < 1000 else 1000
    result = cd.detect(content[0:length])
    return result['encoding']


def get_encoding(file):
    with open(file, mode='rb') as f:
        b = f.readline()
        return cd.detect(b)['encoding']

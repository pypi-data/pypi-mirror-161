# -*- coding: utf-8 -*-
"""
Created on Wed May  2 10:32:16 2018

@author: hu578
"""
import xml.etree.ElementTree as et


def get_xml(file_name):
    root = et.parse(file_name).getroot()  # 获得根节点
    result_list = []
    walk_xml(root, result_list, '')
    return result_list


def walk_xml(root, result_list, tempLists):
    # if tempLists == 'root':
    #    tempLists = ""  
    temp_list = tempLists + ',"' + root.tag + '"'
    result_list.append(temp_list)
    children_node = root.getchildren()
    if len(children_node) == 0:
        return
    for child in children_node:
        walk_xml(child, result_list, temp_list)
    return

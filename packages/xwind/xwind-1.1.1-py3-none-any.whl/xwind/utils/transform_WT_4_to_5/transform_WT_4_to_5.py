import os

import pandas as pd


# 风频矩阵转换
def transform_WTfreq_4_to_5(save_path: str, file_path: str):
    # 生成保存路径
    name = 'transform_' + file_path.split('\\')[-1]
    freq_save_path = save_path + '\\' + name

    # 读取风频文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    # 标签位置获取及替换
    label_index = []  # 存储标签位置
    lines_relabel = []  # 存储标签替换后的内容
    length = len(lines)
    for i in range(length):
        if lines[i].find('Label') == 0:
            label_index.append(i)
            lines_relabel.append(lines[i].replace('Label ', '标签'))
        elif lines[i].find('%') == 1:
            lines_relabel.append(lines[i].replace(' %', '风频(%)'))
        else:
            lines_relabel.append(lines[i])

    # 风频矩阵修改及保存
    with open(freq_save_path, 'w', encoding='utf-8') as f:
        length1 = len(label_index)
        for i in range(length1):
            # 风频矩阵位置
            st_index = label_index[i]
            end_index = st_index + 65

            # 风频矩阵修改
            matrix = []
            for k in range(st_index + 11, end_index - 3):
                string_list = lines_relabel[k].strip().split()
                matrix.append(string_list)
            pd_matrix = pd.DataFrame(matrix[1:], columns=matrix[0], index=list(range(st_index + 12, end_index - 3)))
            pd_matrix = pd_matrix.drop(['%'], axis=1)
            # 保存数据
            for j in range(st_index, end_index):
                if j < st_index + 11:
                    f.writelines(lines_relabel[j])
                    f.writelines('\n')
                elif j == st_index + 11:  # 删除第11行
                    continue
                elif (j > st_index + 11) and (j < end_index - 3):
                    string = pd_matrix.loc[j].values
                    f.writelines('\t'.join(string))
                    f.writelines('\n')
                else:
                    f.writelines(lines_relabel[j])
                    f.writelines('\n')
        print('风频文件 {} 保存完毕'.format(name))


# 湍流矩阵转换
def transform_WTturb_4_to_5(save_path: str, file_path: str):
    # 生成保存路径
    name = 'transform_' + file_path.split('\\')[-1]
    turb_save_path = save_path + '\\' + name

    # 读取湍流文件
    with open(file_path, 'r', encoding='utf-8') as f:
        turb_text = f.readlines()

    # 湍流矩阵转换
    turb_replace_text = []
    length_turb = len(turb_text)
    for i in range(length_turb):
        if turb_text[i].find('Label') == 0:
            turb_replace_text.append(turb_text[i].replace('Label', '标签'))
        elif turb_text[i].find('Added turbulence information') != -1:
            turb_replace_text.append(turb_text[i].replace('Added turbulence information', '附加湍流强度矩阵'))
        elif turb_text[i].find('Effective turbulence information') != -1:
            turb_replace_text.append(turb_text[i].replace('Effective turbulence information', '总体湍流强度信息'))
        elif turb_text[i].find('Characteristic turbulence information') != -1:
            turb_replace_text.append(turb_text[i].replace('Characteristic turbulence information', '特征湍流强度'))
        else:
            turb_replace_text.append(turb_text[i])

    # 湍流文件保存
    with open(turb_save_path, 'w', encoding='utf-8') as f:
        for line in turb_replace_text:
            f.writelines(line)
        print('湍流文件 {} 保存完毕'.format(name))


# 综合结果转换
def transform_WTresult_4_to_5(save_path: str, file_path: str):
    # 生成保存路径
    name = 'transform_' + file_path.split('\\')[-1]
    result_save_path = save_path + '\\' + name

    # 读取综合结果文件
    with open(file_path, 'r', encoding='utf-8') as f:
        result_text = f.read().split('\n')

    # 寻找开始行
    length = len(result_text)
    for i in range(length):
        if result_text[i].find('WT') == 0:
            st_index = i

    # 获取主要信息，创建pandas表格
    matrix = []
    for i in range(st_index, length):
        line = result_text[i].split()
        length1 = len(line)
        if length1 == 204:
            matrix.append(line)
        elif length1 == 203:
            line.insert(0, '0')
            matrix.append(line)

    data = pd.DataFrame(matrix[1:], columns=matrix[0])
    data['NearWT'] = str('A1')
    data['DistM'] = str(500)
    data['DiamR'] = str(141)
    data['DistD'] = str(3.2)

    # 综合结果文件保存
    with open(result_save_path, 'w', encoding='utf-8') as f:
        length = len(result_text)
        length_data = len(data)
        for i in range(st_index + length_data):
            if i < st_index:
                f.writelines(result_text[i])
                f.writelines('\n')
            elif i == st_index:
                string = data.columns.values
                f.writelines('\t'.join(string))
                f.writelines('\n')
            else:
                string = data.loc[i - st_index - 1].values
                f.writelines('\t'.join(string))
                f.writelines('\n')
        print('综合结果文件 {} 保存完毕'.format(name))


def main():
    path = str(input(r'请输入项目所在路径：'))
    projects = os.listdir(path)
    for each in projects:
        file_path = path + '\\' + each
        if os.path.isdir(file_path):
            freq_path = file_path + '\\风频.txt'
            turb_path = file_path + '\\湍流.txt'
            result_path = file_path + '\\综合结果.txt'

            save_path = file_path + '\\transform'
            if not os.path.exists(save_path):
                os.mkdir(save_path)
                print('创建文件夹成功')
            transform_WTfreq_4_to_5(save_path, freq_path)
            transform_WTturb_4_to_5(save_path, turb_path)
            transform_WTresult_4_to_5(save_path, result_path)
        else:
            print('请输入项目所在文件夹路径！')


main

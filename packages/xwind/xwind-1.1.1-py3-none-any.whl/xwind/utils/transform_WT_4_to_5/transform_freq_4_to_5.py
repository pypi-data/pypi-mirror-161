import io

import pandas as pd


def transform_freq(file_path: str) -> io.StringIO:
    """转换风频文件

    Arguments:
        file_path {str} -- 文件路径

    Returns:
        io.StringIO -- 以内存文件形式返回的结果
    """
    output = io.StringIO()
    # 读取风频文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    # 标签位置获取及替换
    label_index = []  # 存储标签位置
    freq_replace = []  # 存储标签替换后的内容
    length = len(lines)
    for i in range(length):
        if lines[i].find('Label') == 0:
            label_index.append(i)
            freq_replace.append(lines[i].replace('Label ', '标签'))
        elif lines[i].find('%') == 1:
            freq_replace.append(lines[i].replace(' %', '风频(%)'))
        else:
            freq_replace.append(lines[i])

    length1 = len(label_index)
    for i in range(length1):
        # 风频矩阵位置
        st_index = label_index[i]
        end_index = st_index + 65

        # 风频矩阵修改
        matrix = []
        for k in range(st_index + 11, end_index - 3):
            string_list = freq_replace[k].strip().split()
            matrix.append(string_list)
        pd_matrix = pd.DataFrame(matrix[1:], columns=matrix[0], index=list(range(st_index + 12, end_index - 3)))
        pd_matrix = pd_matrix.drop(['%'], axis=1)
        # 保存数据
        for j in range(st_index, end_index):
            if j < st_index + 11:
                output.writelines(freq_replace[j])
                output.writelines('\n')
            elif j == st_index + 11:  # 删除第11行
                continue
            elif (j > st_index + 11) and (j < end_index - 3):
                string = pd_matrix.loc[j].values
                output.writelines('\t'.join(string))
                output.writelines('\n')
            else:
                output.writelines(freq_replace[j])
                output.writelines('\n')
    output.seek(0)
    return output

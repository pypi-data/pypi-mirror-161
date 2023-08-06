import io

import pandas as pd


def transform_result(file_path: str) -> io.StringIO:
    """转换综合结果

    Arguments:
        file_path {str} -- 文件路径

    Returns:
        io.StringIO -- 以内存IO的形式返回结果
    """
    output = io.StringIO()
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
    length_data = len(data)
    for i in range(st_index + length_data):
        if i < st_index:
            output.writelines(result_text[i])
            output.writelines('\n')
        elif i == st_index:
            string = data.columns.values
            output.writelines('\t'.join(string))
            output.writelines('\n')
        else:
            string = data.loc[i - st_index - 1].values
            output.writelines('\t'.join(string))
            output.writelines('\n')

    output.seek(0)
    return output

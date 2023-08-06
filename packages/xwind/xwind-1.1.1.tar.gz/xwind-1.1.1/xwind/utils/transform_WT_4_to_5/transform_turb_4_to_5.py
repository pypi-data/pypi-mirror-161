import io


def transform_turb(file_path: str) -> io.StringIO:
    """转换湍流文件

    Arguments:
        file_path {str} -- 文件路径

    Returns:
        io.StringIO -- 以内存IO形式返回的结果
    """
    output = io.StringIO()
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
    for line in turb_replace_text:
        output.writelines(line)

    output.seek(0)
    return output

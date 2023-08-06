import io
import os
from pathlib import Path

from .transform_freq_4_to_5 import transform_freq
from .transform_result_4_to_5 import transform_result
from .transform_turb_4_to_5 import transform_turb


def save(file_save_path, output: io.StringIO):
    with open(file_save_path, 'w', encoding='utf-8') as f:
        f.write(output.getvalue())


path = str(input(r'请输入项目所在路径：'))
projects = os.listdir(path)
for each in projects:
    file_path = Path(path).joinpath(each)
    file_path = path + '\\' + each
    if os.path.isdir(file_path):  # 判断是否为文件夹
        # freq_path = file_path + '\\风频.txt'
        freq_path = Path(file_path).joinpath('风频.txt')
        # turb_path = file_path + '\\湍流.txt'
        turb_path = Path(file_path).joinpath('湍流.txt')
        # result_path = file_path + '\\综合结果.txt'
        result_path = Path(file_path).joinpath('综合结果.txt')

        # save_path = file_path + '\\transform'
        save_path = Path(file_path).joinpath('transform')
        if not os.path.exists(save_path):
            os.mkdir(save_path)

        freq_output = transform_freq(freq_path)
        turb_output = transform_turb(turb_path)
        result_output = transform_result(result_path)

        # freq_save_path = save_path + '\\transform_风频'
        freq_save_path = Path(save_path).joinpath('transform_风频')
        # turb_save_path = save_path + '\\transform_湍流'
        turb_save_path = Path(save_path).joinpath('transform_湍流')
        # result_save_path = save_path + '\\transform_综合结果'
        result_save_path = Path(save_path).joinpath('transform_综合结果')

        save(freq_save_path, freq_output)
        save(turb_save_path, turb_output)
        save(result_save_path, result_output)

    else:
        print('请输入项目所在文件夹路径！')
        break

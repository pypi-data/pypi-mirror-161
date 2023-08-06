import io
import os
import zipfile
from tempfile import SpooledTemporaryFile
from typing import Dict, Tuple, Union, IO

import simplekml as kml


def get_coordinates_from_kml(kml: IO[str]) -> Dict[str, Tuple[float, float]]:
    """从kmz中读取坐标点
        io=open(kml_path,encoding='utf-8')
        result=get_coordinates_from_kml(io)

    Args:
        kml IO[str]: 包含kml内容的IO，意味着你不可以直接传入文件路径，而是先将文件open为IO，这是为了兼顾kmz函数调用的兼容性

    Returns:
        Dict[str,Tuple[float,float]]: 以字典形式返回结果
    """
    from xml.dom.minidom import parse
    dom = parse(kml)
    placemarkers = dom.getElementsByTagName('Placemark')
    result = {}
    id = 0
    for pm in placemarkers:
        name_node = pm.getElementsByTagName('name')
        coords_node = pm.getElementsByTagName('coordinates')
        # 检查两者存在，并且是否未命名
        if coords_node:
            id += 1
            coords = str.split(coords_node[0].firstChild.data, ',')
            if name_node:
                name = name_node[0].firstChild.data
            else:
                name = f'T{id}'
            result[name] = coords[0], coords[1]

    return result


def get_coordinates_from_kmz(kmz: Union[str, io.BytesIO]) -> Dict[str, Tuple[float, float]]:
    """从kmz中提取point点名称与坐标

    Args:
        kmz (Union[str,io.BytesIO]): 文件是以路径或者IO读入的。

    Returns:
        Dict[str,Tuple[float,float]]: 以字典形式返回结果
    """
    # zipfile不支持SpooledTemporaryFile
    kmz_file = zipfile.ZipFile(kmz)
    sf = SpooledTemporaryFile(suffix='.kml', encoding='utf-8')
    sf.write(kmz_file.read('doc.kml'))
    sf.seek(0)
    return get_coordinates_from_kml(sf)


def create_kmz_with_3D_model(points: Dict[str, Tuple[float, float]], heading=0, scale=1.0) -> io.BytesIO:
    """将名称与坐标点转换为带3D模型的kmz，模型的直径是117m，请通过放大系数来调整目标叶轮大小

    Args:
        points (Dict[str,Tuple[float,float]]): 点的字典集合        
        heading (int, optional): 模型朝向. Defaults to 0.
        scale (float, optional): 模型放大系数. Defaults to 1.0.
        
    Returns:
        io.BytesIO: 以IO形式返回
    """

    doc: kml.Kml = kml.Kml()
    dae = os.path.join(os.path.dirname(os.path.realpath(__file__)), '3D-turbine-91mHH.dae')
    doc.addfile(dae)
    # 分开放置点和Model
    folder1: kml.Folder = doc.newfolder(name='points')
    folder2: kml.Folder = doc.newfolder(name='models')
    # 所有点共享一种style，使得生成的文档简洁，每个点单独进行style设置都会生成一个style，即使这些style是一模一样的
    shareStyle = kml.Style()
    shareStyle.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/T.png'
    shareStyle.iconstyle.scale = 1.0
    for n, p in points.items():
        # point
        pnt = folder1.newpoint(name=n, coords=[p])
        pnt.style = shareStyle
        # model
        m: kml.Model = folder2.newmodel(name=n)
        m.altitudemode = kml.AltitudeMode.relativetoground
        m.location = kml.Location(p[0], p[1])
        m.link = kml.Link(href='files/3D-turbine-91mHH.dae')
        real_heading = (heading + 180) % 360
        m.orientation = kml.Orientation(heading=real_heading)
        m.scale = kml.Scale(x=scale, y=scale, z=scale)
    save_io = io.BytesIO()
    doc.savekmz(save_io)
    save_io.seek(0)
    return save_io

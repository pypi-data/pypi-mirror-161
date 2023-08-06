# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xwind',
 'xwind.distribution',
 'xwind.general_functions',
 'xwind.gis',
 'xwind.gis.kml',
 'xwind.gis.objects',
 'xwind.standards',
 'xwind.test1',
 'xwind.turbine',
 'xwind.turbine.properties',
 'xwind.utils',
 'xwind.utils.calculator',
 'xwind.utils.file_io',
 'xwind.utils.rar',
 'xwind.utils.transform_WT_4_to_5',
 'xwind.utils.wt_tools',
 'xwind.utils.wtg_tool',
 'xwind.windfarm',
 'xwind.windfarm.mast',
 'xwind.windfarm.postCFD',
 'xwind.windfarm.postWindFarm',
 'xwind.wt_post_processing']

package_data = \
{'': ['*']}

install_requires = \
['Bottleneck>=1.3.0,<2.0.0',
 'Deprecated',
 'chardet>=4.0.0,<5.0.0',
 'charset-normalizer>=2.0.1,<3.0.0',
 'numba>=0.55.2,<0.56.0',
 'numexpr>=2.7.3,<3.0.0',
 'numpy>=1.20.0,<2.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.3.1,<2.0.0',
 'scipy>=1.7.1,<2.0.0',
 'simplekml>=1.3.6,<2.0.0']

setup_kwargs = {
    'name': 'xwind',
    'version': '1.1.1',
    'description': '',
    'long_description': "# 开发者注意事项\n由于使用了numba，在m1 mac上，需要使用homebrew安装llvm@11，然后指定'''export LLVM_CONFIG=/opt/homebew/opt/llvm@11/bin/llvm-config'''，否在会卡在llvmlite安装上报错。",
    'author': 'HuQin',
    'author_email': 'hu578344563@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from setuptools import find_packages, setup
from os import path as os_path
import time

# 这里是基本的信息

name = 'tkitAutoRewriter'  # 修改包名字-
version = '0.0.0.1' + str(time.time())[:8]
description = 'Terry toolkit sdk for AutoRewriter ,'
author = 'Terry Chan'
author_email = 'napoler2008@gmail.com'
url = 'https://www.terrychan.org/2022/07/%e8%8b%b1%e6%96%87%e5%86%85%e5%ae%b9%e8%87%aa%e5%8a%a8%e9%87%8d%e5%86%99sdk/'

copyright = '2021, Terry Chan'
language = 'zh_cn'

this_directory = os_path.abspath(os_path.dirname(__file__))
"""帮助[https://www.notion.so/6bade2c6a5f4479f82a4e67eafcebb3a]
上传到anaconda
https://docs.anaconda.com/anacondaorg/user-guide/tasks/work-with-packages/

    """


# 读取文件内容
def read_file(filename):
    with open(os_path.join(this_directory, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


# 获取依赖
def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]


# long_description="""

# 这里是说明
# 一个创建库的demo
# http://www.terrychan.org/python_libs_demo/
# """


long_description = read_file("README.md")
setup(
    name=name,  # 修改包名字-
    version=version,
    description=description,
    author=author,
    author_email=author_email,
    url=url,
    # install_requires=read_requirements('requirements.txt'),  # 指定需要安装的依赖
    long_description=long_description,
    long_description_content_type="text/markdown",
    # 依赖文件
    install_requires=[
        'tqdm>=4.64.0',
        'sentence-splitter>=1.4',
        'requests>=2.28.1'

    ],
    packages=['tkitAutoRewriter'],  # 扫描的目录
    nclude_package_data=True,  # 打包包含静态文件标识
)

"""
pip freeze > requirements.txt
python3 setup.py sdist
#python3 setup.py install
python3 setup.py sdist upload
"""
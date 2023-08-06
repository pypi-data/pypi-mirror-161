# encoding: utf-8
"""
@project: resource->config
@author: 孙楷炎
@synopsis: 文件模块配置文件
@created_time: 2022/5/28 12:19
"""

import os
import time
# from pathlib import Path  # for Python 3.8

from main.settings import STATIC_URL, BASE_DIR

# resource模块应放在apps.resource目录下
# BASE_DIR = Path(__file__).resolve().parent.parent.parent # for Python 3.8 项目根目录
# BASE_DIR =os.path.abspath(os.path.join(os.getcwd(), '.'))  # 项目根目录

today = time.strftime('%Y-%m', time.localtime(time.time()))
FILE_UPLOAD_DIR = STATIC_URL + "/upload/file/" + today + "/"
IMAGE_UPLOAD_DIR = STATIC_URL + "/upload/image/" + today + "/"

# file_format_list:  False  # false 不限制文件类型 TODO 逻辑宏常量应该转成大写
file_format_list = False
img_format_list = ('jpg', 'jpeg', 'gif', 'png', 'svg')
host = ''

# 资源文件路径。注：此路径需包含在settings.py的STATICFILES_DIRS中
RESOURCE_FILES_DIR = os.path.join(BASE_DIR, "resource_files")

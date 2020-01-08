# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2020/1/8 16:49
# Author :  Richard
# File   :  views.py

'''
人群密度信息的识别
'''

# 导入蓝图程序用于构建路由
from . import recognize
# 导入实体列 用户操作数据库
from ..models import *


@recognize.route("/")
def recognize():
    '''
    1、人脸的检测
    2、人脸的保存和人脸特征的保存
    3、周期的返回人口信息
    :return: json格式数据
    '''
    return "人群密度检测"

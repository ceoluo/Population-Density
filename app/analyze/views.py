# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2020/1/8 16:58
# Author :  Richard
# File   :  views.py

# 导入蓝图程序用于构建路由
from . import analyze
# 导入实体列 用户操作数据库
from ..models import *


@analyze.route("/")
def analyze():
    '''
    1、与后台协商完成数据的分析
    2、分析后的信息的可视化
    :return :json格式信息或者将生成的图片保存至静态文件夹
    '''
    return "数据分析与可视化"

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2020/1/8 16:42
# Author :  Richard
# File   :  views.py

from flask import session

# 导入蓝图程序用于构建路由
from . import main
# 导入实体列 用户操作数据库
from ..models import *


@main.route("/")
def index():
    '''
    1、完成用户登录注册功能
    2、完成数据汇总、存储
    3、完成信息的发布
    :return :json格式信息
    '''
    return '公共交通人口密度识别系统'

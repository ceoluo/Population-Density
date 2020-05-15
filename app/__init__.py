# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2020/1/8 14:34
# Author :  Richard
# File   :  __init__.py

'''
# app下的__init__.py文件
# 将整个应用初始化
# 主要工作
#     1：构建flask应用以及各种配置
#     2：构建SQLAlchemy的应用
'''
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
import os

# 将pymysql注册为MySQL的驱动
pymysql.install_as_MySQLdb()

db = SQLAlchemy()


# 创建app实例
def create_app():
    '''
    配置app的资源目录、数据库、session等信息
    :return: app对象
    '''
    # 获取项目路径
    BASE_DIR = os.path.dirname(__file__)
    # app目录路径
    # APP_DIR = os.path.join(BASE_DIR, 'app')
    # 静态资源目录路径
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    # 模板目录路径
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
    # 定义app实例，绑定静态资源和模板路径
    app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATES_DIR)
    # 配置启动模式为调试模式
    app.config["DEBUG"] = False
    # 将SQLALCHWMY的追踪对象的修改设置为False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # 以URL的格式配置数据库的连接
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Hello@world@123.57.55.107:3306/PopulationDensity"
    # 配置session所需要的秘钥
    app.config["SECRET_KEY"] = "passwordkey"
    # 查询时在控制台打印出原始SQL语句
    app.config['SQLALCHEMY_ECHO'] = False
    # 返回数据支持中文
    app.config['JSON_AS_ASCII'] = False
    # 数据库的初始化
    # 将app程序与数据库绑定起来
    db.app = app
    db.init_app(app)
    # 将main蓝图程序与app关联到一起
    from .main import main as main_blueprint
    from .analyze import analyze as analyze_blueprint
    from .recognize import recognize as recognize_blueprint
    # 在app中注册上述蓝图
    app.register_blueprint(main_blueprint, url_prefix='/')
    app.register_blueprint(analyze_blueprint, url_prefix='/analyze')
    app.register_blueprint(recognize_blueprint, url_prefix='/recognize')
    # 设置session的生命周期
    app.permanent_session_lifetime = datetime.timedelta(seconds=10 * 60)
    return app


if __name__ == "__main__":
    app = create_app()
    # 在本机上运行改app实例
    app.run(host='0.0.0.0', port=80)

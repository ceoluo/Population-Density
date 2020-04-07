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
# 处理请求
from flask import request,jsonify
import time
import os
import cv2
import numpy as np

@recognize.route("/")
def index():
    '''
    1、人脸的检测
    2、人脸的保存和人脸特征的保存
    3、周期的返回人口信息
    :return: json格式数据
    '''
    return "人群密度检测"

'''
@recognize.route("add_user")
def add_user():
    user = User(phone='18208381239',
                user_name="忠孝",
                email="userzhongxiao@163.com",
                password="Hello@world",sex=1,
                head_img="Population-density.jpg",
                address="四川成都",
                longitude=None,
                latitude=None,
                born_date="1997-07-20",
                production="I'm a good man!")
    user.save()
    return "200"

@recognize.route("/add_route")
def add_route():
    route = Route("2号线")
    route.save()
    return "添加地铁线路成功！"

@recognize.route("/add_station")
def add_station():
    station = Station(station_name="犀浦快铁站",station_type="1",
                      longitude=None,latitude=None)
    station.save()
    station = Station("西华大学南大门站",station_type="1",
                      longitude=None,latitude=None)
    station.save()
    station = Station("西华大学西门站",station_type="1",
                      longitude=None,latitude=None)
    station.save()
    station = Station("天河路",station_type="1",
                      longitude=None,latitude=None)
    station.save()
    station = Station("春熙路",station_type="1",
                      longitude=None,latitude=None)
    station.save()
    return "添加站点成功"

@recognize.route("/add_route_station")
def add_route_station():
    route_station = Route_station(route_id=1,station_id=1,station_order=1)
    route_station.save()
    route_station = Route_station(route_id=1,station_id=4,station_order=2)
    route_station.save()
    route_station = Route_station(route_id=1,station_id=5,station_order=3)
    route_station.save()
    return  "添加关联站点成功"

@recognize.route("/add_bus")
def add_bus():
    bus = Bus(route_id=1,user_id=1,type_id=1,permit_passengers=1,start_date="2020-1-1",belong_company="天府通公交公司")
    bus.save()
    return "添加公交成功！"
'''

# 接受检测终端的数据，并生成时间戳保存到数据库
@recognize.route("/save_detection",methods=['post'])
def save_detection():
    # data = {"type_code": type_code, "area_id": area_id, "land_mark": land_mark, "face_img": face_img}
    # 获取时间戳
    # t = time.time()*1000
    t = int(time.time()*1000)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    # 检测终端所在地点的类型(0:公交, 1:公交站)
    type_code_d = {0:"0-bus",1:"1-station"}
    type_code = request.form.get("type_code")
    type_code = int(type_code)
    # 检测地域的id
    area_id = request.form.get("area_id")
    area_id = int(area_id)
    # 脸部标定点
    land_mark = request.form.get("land_mark")
    print("land_mark:",land_mark)
    # 脸部图像
    face_img = request.form.get("face_img")
    # 构造人脸图片存储路径
    cwd_dir = os.path.dirname(os.path.realpath(__file__))
    all_face_picture_dir = os.path.join(cwd_dir, 'all-face-pictures')
    dir_name = os.path.join(all_face_picture_dir,type_code_d[type_code])
    face_picture_dir = os.path.join(dir_name,str(area_id))
    if not os.path.isdir(face_picture_dir):
        os.mkdir(face_picture_dir)
    face_picture_name = str(t)+'.jpg'
    face_picture_path = os.path.join(face_picture_dir,face_picture_name)
    # 保存人脸图片到服务器
    face_img = np.array(eval(face_img))
    cv2.imwrite(face_picture_path,face_img)
    # 添加passenger
    passenger = Passenger(face_landmark=land_mark,picture_name=face_picture_name)
    passenger.save()
    # 获取当前添加的乘客的id
    passenger_id = passenger.passenger_id
    print("p_id:",passenger_id)
    # 添加关联站点或公交
    if type_code == 0:
        bus_passenger = Bus_passenger(bus_id=area_id,passenger_id=passenger_id,timestamp=timestamp)
        bus_passenger.save()
    elif type_code == 1:
        station_passenger = Station_passenger(station_id=area_id,passenger_id=passenger_id,timestamp=timestamp)
        station_passenger.save()
    else:
        return "404"
    return "200"

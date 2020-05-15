# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2020/1/8 16:49
# Author :  Richard
# File   :  views.py

'''
人群密度信息的识别
'''

# 导入蓝图程序用于构建路由
import heapq

from app.config import all_face_picture_dir, all_scene_picture_dir
from . import recognize
# 导入实体列 用户操作数据库
from ..models import *
# 处理请求
from flask import request, jsonify, url_for, Response
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


@recognize.route("add_user")
def add_user():
    user = User(phone='18208381239',
                user_name="忠孝",
                email="userzhongxiao@163.com",
                password="Hello@world", sex=1,
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
    # route = Route("1号线")
    # route.save()
    route = Route("2号线")
    route.save()
    return "添加地铁线路成功！"


@recognize.route("/add_station")
def add_station():
    station = Station(station_name="犀浦快铁站", station_type="1",
                      longitude=None, latitude=None)
    station.save()
    station = Station("西华大学南大门站", station_type="1",
                      longitude=None, latitude=None)
    station.save()
    station = Station("西华大学西门站", station_type="1",
                      longitude=None, latitude=None)
    station.save()
    station = Station("天河路", station_type="1",
                      longitude=None, latitude=None)
    station.save()
    station = Station("春熙路", station_type="1",
                      longitude=None, latitude=None)
    station.save()
    return "添加站点成功"


@recognize.route("/add_route_station")
def add_route_station():
    route_station = Route_station(route_id=1, station_id=1, station_order=1)
    route_station.save()
    route_station = Route_station(route_id=1, station_id=4, station_order=2)
    route_station.save()
    route_station = Route_station(route_id=1, station_id=5, station_order=3)
    route_station.save()
    return "添加关联站点成功"


@recognize.route("/add_bus")
def add_bus():
    bus = Bus(route_id=1, user_id=1, type_id=1, permit_passengers=100, start_date="2020-1-1", belong_company="天府通公交公司")
    bus.save()
    bus = Bus(route_id=2, user_id=1, type_id=1, permit_passengers=50, start_date="2020-1-1", belong_company="天府通公交公司")
    bus.save()
    bus = Bus(route_id=2, user_id=1, type_id=1, permit_passengers=80, start_date="2020-1-1", belong_company="天府通公交公司")
    bus.save()
    bus = Bus(route_id=2, user_id=1, type_id=1, permit_passengers=60, start_date="2020-1-1", belong_company="天府通公交公司")
    bus.save()
    return "添加公交成功！"


# 接受检测终端的数据，并生成时间戳保存到数据库
@recognize.route("/save_face", methods=['post'])
def save_face():
    # data = {"type_code": type_code, "area_id": area_id, "land_mark": land_mark, "face_img": face_img}
    # 获取时间戳
    # t = time.time()*1000
    t = int(time.time() * 1000)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    # 检测终端所在地点的类型(0:公交, 1:公交站)
    type_code_d = {0: "0-bus", 1: "1-station"}
    type_code = request.form.get("type_code")
    type_code = int(type_code)
    # 检测地域的id
    area_id = request.form.get("area_id")
    area_id = int(area_id)
    # 脸部标定点
    land_mark = request.form.get("land_mark")
    print("land_mark:", land_mark)
    # 脸部图像
    face_img = request.form.get("face_img")

    dir_name = os.path.join(all_face_picture_dir, type_code_d[type_code])
    face_picture_dir = os.path.join(dir_name, str(area_id))
    if not os.path.isdir(face_picture_dir):
        os.mkdir(face_picture_dir)
    face_picture_name = str(t) + '.jpg'
    face_picture_path = os.path.join(face_picture_dir, face_picture_name)
    # 保存人脸图片到服务器
    face_img = np.array(eval(face_img))
    cv2.imwrite(face_picture_path, face_img)
    # 添加passenger
    passenger = Passenger(face_landmark=land_mark, picture_name=face_picture_name)
    passenger.save()
    # 获取当前添加的乘客的id
    passenger_id = passenger.passenger_id
    print("p_id:", passenger_id)
    # 添加关联站点或公交
    if type_code == 0:
        bus_passenger = Bus_passenger(bus_id=area_id, passenger_id=passenger_id, timestamp=timestamp)
        bus_passenger.save()
    elif type_code == 1:
        station_passenger = Station_passenger(station_id=area_id, passenger_id=passenger_id, timestamp=timestamp)
        station_passenger.save()
    else:
        return "404"
    return "200"

# 接收现场图片，以时间戳格式命名保存到服务器对应站点或公交目录下的scene中
@recognize.route("/save_scene", methods=['post'])
def save_scene():
    # data = {"type_code": type_code, "area_id": area_id, "land_mark": land_mark, "face_img": face_img}
    # 获取时间戳
    # t = time.time()*1000
    t = int(time.time() * 1000)
    # timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    # 检测终端所在地点的类型(0:公交, 1:公交站)
    type_code_d = {0: "0-bus", 1: "1-station"}
    type_code = request.form.get("type_code")
    type_code = int(type_code)
    # 检测地域的id
    area_id = request.form.get("area_id")
    area_id = int(area_id)
    # 场景图像
    scene_img = request.files["scene_img"]
    dir_name = os.path.join(all_scene_picture_dir, type_code_d[type_code])
    scene_picture_dir = os.path.join(dir_name, str(area_id))
    if not os.path.isdir(scene_picture_dir):
        os.mkdir(scene_picture_dir)
    scene_picture_name = str(t) + '.jpg'
    scene_picture_path = os.path.join(scene_picture_dir, scene_picture_name)
    # 保存图片到服务器
    scene_img.save(scene_picture_path)
    return "200"


@recognize.route("/get_scene/<image_name>", methods=['get'])
def get_scene(image_name):
    res = {"code": 200, "msg": "请求成功", "data": None}
    # 从请求中获取参数
    # 检测终端所在地点的类型(0:公交, 1:公交站)
    type_code_d = {0: "0-bus", 1: "1-station"}
    type_code = request.args.get('type_code')
    type_code = int(type_code)
    area_id = request.args.get('area_id')
    area_id = int(area_id)
    n_images = request.args.get('n_images')
    n_images = int(n_images)
    # print(type_code, area_id, n_images)
    # 参数校验
    if type_code is None or area_id is None or type_code not in (0, 1):
        res['code'] = 400
        res['msg'] = "请检查参数是否正确！"
        return jsonify(res)
    # area_id校验

    # 查找该场景最近的k张图片
    dir_name = os.path.join(all_scene_picture_dir, type_code_d[type_code])
    scene_picture_dir = os.path.join(dir_name, str(area_id))
    print(scene_picture_dir)
    if image_name == 'image_name':
        print(os.listdir(scene_picture_dir))
        images_list = [int(t.split('.')[0]) for t in os.listdir(scene_picture_dir)]
        print(images_list)
        if n_images > len(images_list):
            n_images = len(images_list)
        max_nlargest = heapq.nlargest(n_images, images_list)
        # 返回数据
        max_nlargest = [str(img) + '.jpg' for img in max_nlargest]
        data = {"base_url": "/get_scene/", "n_images": max_nlargest}
        res['code'] = 200
        res['msg'] = "请求成功！"
        res['data'] = data
        return jsonify(res)
    else:
        image_path = os.path.join(scene_picture_dir, image_name)
        print(image_path)
        with open(image_path, 'rb') as f:
            image = f.read()
        res = Response(image, mimetype='image/jpg')
        res.status_code = 200
        return res

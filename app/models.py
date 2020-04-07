# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2020/1/8 17:39
# Author :  Richard
# File   :  models.py

'''
操作数据库
'''

# 当前项目相关的模型文件 所有 实体类
from sqlalchemy import UniqueConstraint

from . import db



'''
/*==============================================================*/
/* Table: admin                                                 */
/*==============================================================*/
'''


class Admin(db.Model):
    __tablename__ = "admin"
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    delete_type = db.Column(db.SMALLINT, nullable=False, default=0, comment='(0:正常，1:删除)')

    def __init__(self, delete_type):
        self.delete_type = delete_type

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<Admin:%r>' % self.__tablename__


'''
/*==============================================================*/
/* Table: bus                                                   */
/*==============================================================*/
'''


class Bus(db.Model):
    '''
    comment= '公交车（公交车id、公交车类型、准载客数、司机id、投运时间、运行路线、所属公司）';
    '''
    __tablename__ = "bus"
    bus_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    route_id = db.Column(db.Integer, db.ForeignKey("route.route_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), comment='用户编号')
    type_id = db.Column(db.Integer, nullable=False)
    delete_type = db.Column(db.SMALLINT, nullable=False, default=0, comment='(0:正常，1:删除)')
    permit_passengers = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DATE)
    belong_company = db.Column(db.String(30))
    # 反向引用 user_bus
    user_bus = db.relationship("User_bus", backref="bus", lazy="dynamic")
    # 反向引用 bus_passenger
    bus_passenger = db.relationship("Bus_passenger", backref="bus", lazy="dynamic")

    def __init__(self, route_id, user_id, type_id, delete_type=0, permit_passengers=None, start_date=None,
                 belong_company=None):
        self.route_id = route_id
        self.user_id = user_id
        self.type_id = type_id
        self.delete_type = delete_type
        self.permit_passengers = permit_passengers
        self.start_date = start_date
        self.belong_company = belong_company

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<Bus:%r>' % self.__tablename__


'''
/*==============================================================*/
/* Table: bus_passenger                                         */
/*==============================================================*/
'''


class Bus_passenger(db.Model):
    __tablename__ = "bus_passenger"
    bus_passenger = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bus_id = db.Column(db.Integer, db.ForeignKey("bus.bus_id"))
    passenger_id = db.Column(db.Integer, db.ForeignKey("passenger.passenger_id"))
    timestamp = db.Column(db.TIMESTAMP)

    def __init__(self, bus_id, passenger_id, timestamp):
        self.bus_id = bus_id
        self.passenger_id = passenger_id
        self.timestamp = timestamp

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<Bus_passenger:%r>' % self.__tablename__


'''
/*==============================================================*/
/* Table: passenger                                             */
/*==============================================================*/
'''


class Passenger(db.Model):
    '''
    comment= '乘客（乘客id、性别、年龄段、是否戴眼镜、是否戴帽子、是否涂口红、是否戴口罩、面部表情、特征矩阵）';
    '''
    __tablename__ = "passenger"
    passenger_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    delete_type = db.Column(db.SMALLINT, nullable=False, default=0, comment='(0:正常，1:删除)')
    sex = db.Column(db.Boolean)
    age_level = db.Column(db.SMALLINT)
    is_glasses = db.Column(db.Boolean)
    is_hat = db.Column(db.Boolean)
    is_mask = db.Column(db.Boolean)
    is_lipstick = db.Column(db.Boolean)
    face_expression = db.Column(db.SMALLINT)
    future_matrix = db.Column(db.Text)
    face_landmark = db.Column(db.String(300))
    picture_name = db.Column(db.String(50))
    # 反向引用 user_passenger
    user_passenger = db.relationship("User_passenger", backref="passenger", lazy="dynamic")
    # 反向引用 bus_passenger
    bus_passenger = db.relationship("Bus_passenger", backref="passenger", lazy="dynamic")
    # 反向引用 bus_passenger
    station_passenger = db.relationship("Station_passenger", backref="passenger", lazy="dynamic")

    def __init__(self, face_landmark, picture_name,delete_type=0, sex=0,
                 age_level=1, is_glasses=0, is_hat=0, is_mask=0,
                 is_lipstick=0, face_expression=0, future_matrix='0'*128):
        self.face_landmark = face_landmark
        self.picture_name = picture_name
        self.delete_type = delete_type
        self.sex = sex
        self.age_level = age_level
        self.is_glasses = is_glasses
        self.is_hat = is_hat
        self.is_mask = is_mask
        self.is_lipstick = is_lipstick
        self.face_expression = face_expression
        self.future_matrix = future_matrix

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<Passenger:%r>' % self.__tablename__


'''
/*==============================================================*/
/* Table: route                                                 */
/*==============================================================*/
'''


class Route(db.Model):
    __tablename__ = "route"
    route_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    route_name = db.Column(db.CHAR(20))
    # 反向引用 bus
    bus = db.relationship("Bus", backref="route", lazy="dynamic")
    # 反向引用 route_station
    route_station = db.relationship("Route_station", backref="route", lazy="dynamic")

    def __init__(self, route_name):
        self.route_name = route_name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<Route:%r>' % self.__tablename__

'''
/*==============================================================*/
/* Table: route_station                                         */
/*==============================================================*/
'''


class Route_station(db.Model):
    __tablename__ = "route_station"
    route_station_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    route_id = db.Column(db.Integer, db.ForeignKey("route.route_id"))
    station_id = db.Column(db.Integer, db.ForeignKey("station.station_id"))
    station_order = db.Column(db.SMALLINT)

    def __init__(self, route_id, station_id, station_order):
        self.route_id = route_id
        self.station_id = station_id
        self.station_order = station_order

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<Route_station:%r>' % self.__tablename__

'''
/*==============================================================*/
/* Table: station                                               */
/*==============================================================*/
'''


class Station(db.Model):
    '''
    comment= '站点(站点id、类型id、站点名称、经度、纬度)';
    '''
    __tablename__ = "station"
    station_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    station_name = db.Column(db.String(20), nullable=False)
    delete_type = db.Column(db.SMALLINT, nullable=False, default=0, comment='(0:正常，1:删除)')
    station_type = db.Column(db.SMALLINT, nullable=False)
    longitude = db.Column(db.DECIMAL(10, 6))
    latitude = db.Column(db.DECIMAL(10, 6))
    # 反向引用 route_station
    route_station = db.relationship("Route_station", backref="station", lazy="dynamic")
    # 反向引用 station_passenger
    station_passenger = db.relationship("Station_passenger", backref="station", lazy="dynamic")
    # 反向引用 user_station
    user_station = db.relationship("User_station", backref="station", lazy="dynamic")

    def __init__(self, station_name, station_type, longitude=None, latitude=None, delete_type=0):
        self.station_name = station_name
        self.station_type = station_type
        self.delete_type = delete_type
        self.longitude = longitude
        self.latitude = latitude

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<Station:%r>' % self.__tablename__

'''
/*==============================================================*/
/* Table: station_passenger                                     */
/*==============================================================*/
'''


class Station_passenger(db.Model):
    __tablename__ = "station_passenger"
    station_passenger = db.Column(db.Integer, primary_key=True, autoincrement=True)
    station_id = db.Column(db.Integer, db.ForeignKey("station.station_id"))
    passenger_id = db.Column(db.Integer, db.ForeignKey("passenger.passenger_id"))
    timestamp = db.Column(db.TIMESTAMP)

    def __init__(self, station_id, passenger_id, timestamp):
        self.station_id = station_id
        self.passenger_id = passenger_id
        self.timestamp = timestamp

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<Station_passenger:%r>' % self.__tablename__

'''
/*==============================================================*/
/* Table: user                                                  */
/*==============================================================*/
'''


class User(db.Model):
    '''
    comment= '用户（电话、用户id、用户名、密码、删除类型、邮箱、性别、头像、家庭住址、经度、 纬度、出生日期）  ';
    '''
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户编号')
    phone = db.Column(db.CHAR(11), nullable=False, comment='电话')
    user_name = db.Column(db.String(11), nullable=False, comment='用户名')
    email = db.Column(db.String(50))
    password = db.Column(db.CHAR(32), nullable=False, comment='密码')
    delete_type = db.Column(db.SMALLINT, nullable=False, default=0, comment='(0:正常，1:删除)')
    sex = db.Column(db.Integer, nullable=False, comment='性别（0女，1男）')
    head_img = db.Column(db.String(200), comment='头像')
    address = db.Column(db.String(100))
    born_date = db.Column(db.DATE, nullable=False, comment='出生日期')
    longitude = db.Column(db.DECIMAL(10, 6),nullable=True)
    latitude = db.Column(db.DECIMAL(10, 6),nullable=True)
    production = db.Column(db.String(500))
    __table_args__ = (
        UniqueConstraint('phone', 'user_name'),  # 电话和用户名唯一
    )
    # 反向引用 user_station
    user_station = db.relationship("User_station", backref="user", lazy="dynamic")
    # 反向引用 user_bus
    user_bus = db.relationship("User_bus", backref="user", lazy="dynamic")
    # 反向引用 user_passenger
    user_passenger = db.relationship("User_passenger", backref="user", lazy="dynamic")

    def __init__(self, phone, user_name, email, password, sex, head_img,
                 address, born_date, longitude, latitude, production,
                 delete_type=0):
        self.phone = phone
        self.user_name = user_name
        self.email = email
        self.password = password
        self.sex = sex
        self.head_img = head_img
        self.address = address
        self.born_date = born_date
        self.longitude = longitude
        self.latitude = latitude
        self.production = production
        self.delete_type = delete_type

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<User:%r>' % self.__tablename__

'''
/*==============================================================*/
/* Table: user_bus                                              */
/*==============================================================*/
'''


class User_bus(db.Model):
    __tablename__ = "user_bus"
    user_bus = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), comment='用户编号')
    bus_id = db.Column(db.Integer, db.ForeignKey("bus.bus_id"))
    timestamp = db.Column(db.TIMESTAMP)

    def __init__(self, user_id, bus_id, timestamp):
        self.user_id = user_id
        self.bus_id = bus_id
        self.timestamp = timestamp

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<User_bus:%r>' % self.__tablename__

'''
/*==============================================================*/
/* Table: user_passenger                                        */
/*==============================================================*/
'''


class User_passenger(db.Model):
    __tablename__ = "user_passenger"
    user_passenger = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), comment='用户编号')
    passenger_id = db.Column(db.Integer, db.ForeignKey("passenger.passenger_id"))
    timestamp = db.Column(db.TIMESTAMP)

    def __init__(self, user_id, passenger_id, timestamp):
        self.user_id = user_id
        self.passenger_id = passenger_id
        self.timestamp = timestamp

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<User_passenger:%r>' % self.__tablename__


'''
/*==============================================================*/
/* Table: user_station                                          */
/*==============================================================*/
'''


class User_station(db.Model):
    __tablename__ = "user_station"
    user_station = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), comment='用户编号')
    station_id = db.Column(db.Integer, db.ForeignKey("station.station_id"))
    timestamp = db.Column(db.TIMESTAMP)

    def __init__(self, user_id, station_id, timestamp):
        self.user_id = user_id
        self.station_id = station_id
        self.timestamp = timestamp

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<User_station:%r>' % self.__tablename__

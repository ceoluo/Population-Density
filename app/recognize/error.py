# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2020/4/2 17:10
# Author :  Richard
# File   :  error.py

from flask import abort
from . import recognize
# from ..models import *


@recognize.route("/error_401")
def error_401():
    return abort(401)

@recognize.route("/error_404")
def error_404():
    return abort(404)

@recognize.route("/error_501")
def error_501():
    return abort(501)

@recognize.errorhandler(404)
def error_action(e):
    return "该请求打瞌睡了！。。。。"
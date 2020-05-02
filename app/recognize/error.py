# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2020/4/2 17:10
# Author :  Richard
# File   :  error.py

from flask import abort, jsonify
from . import recognize
# from ..models import *


@recognize.errorhandler(404)
def error_404(error):
    """这个handler可以catch住所有abort(404)以及找不到对应router的处理请求"""
    response = dict(status=0, message="404 Not Found")
    return jsonify(response), 404


@recognize.errorhandler(Exception)
def error_500(error):
    """这个handler可以catch住所有的abort(500)和raise exeception."""
    response = dict(status=0, message="500 Error")
    return jsonify(response), 500


class MyError(Exception):
    """自定义错误类"""
    pass


@recognize.errorhandler(MyError)
def MyErrorHandle(error):
    response = dict(status=0, message="400 Error")
    return jsonify(response), 400
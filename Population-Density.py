# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2020/1/8 17:20
# Author :  Richard
# File   :  Population-Density.py

from app import create_app

# 创建app,启动app
# app = create_app
# app.run()


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=80)

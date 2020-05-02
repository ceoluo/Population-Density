# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2020/5/1 18:39
# Author :  Richard
# File   :  config.py
import os

# static文件夹路径
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

# 人脸图片存储路径
all_face_picture_dir = os.path.join(STATIC_DIR, 'recognized_images', 'all-face-pictures')

# 场景图片存储路径
all_scene_picture_dir = os.path.join(STATIC_DIR, 'recognized_images', 'all-scene-pictures')
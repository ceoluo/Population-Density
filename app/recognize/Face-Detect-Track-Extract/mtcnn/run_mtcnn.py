# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2020/3/29 16:51
# Author :  Richard
# File   :  run_mtcnn.py
import os
import time

import cv2
from mtcnn.train import config


def run_mtcnn(frame, mtcnn_detector):
    if config.input_mode == '1':
        # 下面两行为跟踪时调用
        boxes_c, landmarks = mtcnn_detector.detect(frame)
        return boxes_c, landmarks

    if config.input_mode == '2':
        # VideoCapture()中参数是0，表示打开笔记本的内置摄像头，
        # 参数是视频文件路径则打开视频，如cap = cv2.VideoCapture(“../test.avi”)
        # cap = cv2.VideoCapture(
        #     "D:/Project/Population-Density/app/recognize/tensorflow-MTCNN/video/VID_20191229_143420.mp4")
        cap = cv2.VideoCapture(0)
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        print("weigth: ****", cap.get(3))
        print("heigt: ***", cap.get(4))
        # sys.exit(1)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # fourcc = -1
        out = cv2.VideoWriter(config.out_path + 'out2.avi', fourcc, 10, (1152, 648))
        while True:
            t1 = cv2.getTickCount()
            ret, frame = cap.read()
            print("old_shape: ", frame.shape)
            frame = cv2.resize(frame, (int(frame.shape[1] * 0.6), int(frame.shape[0] * 0.6)),
                               interpolation=cv2.INTER_AREA)
            print("new_shape: ", frame.shape)
            boxes_c, landmarks = None, None
            if ret == True:
                boxes_c, landmarks = mtcnn_detector.detect(frame)
                t2 = cv2.getTickCount()
                t = (t2 - t1) / cv2.getTickFrequency()
                fps = 1.0 / t
                print("fps: ", fps)
            return boxes_c, landmarks

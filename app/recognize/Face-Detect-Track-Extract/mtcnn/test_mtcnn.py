# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2020/3/29 16:51
# Author :  Richard
# File   :  run_mtcnn.py
import os
import time

from detection.MtcnnDetector import MtcnnDetector
from detection.detector import Detector
from detection.fcn_detector import FcnDetector
from train.model import P_Net, R_Net, O_Net
import cv2
from mtcnn.train import config


def test_mtcnn(test_PNet):
    # test_mode = config.test_mode
    test_mode = test_PNet
    thresh = config.thresh
    min_face_size = config.min_face
    stride = config.stride
    detectors = [None, None, None]
    # 模型放置位置
    cwd_path = os.path.dirname(os.path.abspath(__file__))
    model_path = [os.path.join(cwd_path, 'model/PNet/'), os.path.join(cwd_path, 'model/RNet/'),
                  os.path.join(cwd_path, 'model/ONet')]
    batch_size = config.batches
    PNet = FcnDetector(P_Net, model_path[0])
    detectors[0] = PNet

    if test_mode in ["RNet", "ONet"]:
        RNet = Detector(R_Net, 24, batch_size[1], model_path[1])
        detectors[1] = RNet

    if test_mode == "ONet":
        ONet = Detector(O_Net, 48, batch_size[2], model_path[2])
        detectors[2] = ONet

    mtcnn_detector = MtcnnDetector(detectors=detectors, min_face_size=min_face_size,
                                   stride=stride, threshold=thresh)
    out_path = config.out_path

    if config.input_mode == '1':
        # 选用图片
        path = config.test_dir
        # 下面两行为跟踪时调用
        # boxes_c, landmarks = mtcnn_detector.detect(frame)
        # return boxes_c, landmarks
        # 下面代码为单独测试MTCNN时调用
        for item in os.listdir(path):
            img_path = os.path.join(path, item)
            img = cv2.imread(img_path)
            img = cv2.resize(img, (0, 0), fx=0.7, fy=0.7)
            t1 = time.time()
            boxes_c, landmarks = mtcnn_detector.detect(img)
            t2 = time.time()
            print("per_picture_time：", t2 - t1)
            for i in range(boxes_c.shape[0]):
                bbox = boxes_c[i, :4]
                score = boxes_c[i, 4]
                corpbbox = [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])]
                # 画人脸框
                cv2.rectangle(img, (corpbbox[0], corpbbox[1]),
                              (corpbbox[2], corpbbox[3]), (255, 0, 0), 1)
                # 判别为人脸的置信度
                cv2.putText(img, '{:.2f}'.format(score),
                            (corpbbox[0], corpbbox[1] - 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # 画关键点
            for i in range(landmarks.shape[0]):
                for j in range(len(landmarks[i]) // 2):
                    cv2.circle(img, (int(landmarks[i][2 * j]), int(int(landmarks[i][2 * j + 1]))), 2, (0, 0, 255))
            cv2.imshow('im', img)
            k = cv2.waitKey(0) & 0xFF
            if k == 27:
                cv2.imwrite(out_path + item, img)
        cv2.destroyAllWindows()

    if config.input_mode == '2':
        # VideoCapture()中参数是0，表示打开笔记本的内置摄像头，
        # 参数是视频文件路径则打开视频，如cap = cv2.VideoCapture(“../test.avi”)
        # cap = cv2.VideoCapture(
        #     "D:/Project/Population-Density/app/recognize/tensorflow-MTCNN/video/VID_20191229_143420.mp4")
        cap = cv2.VideoCapture(0)
        print("weigth: ****", cap.get(3))
        print("heigt: ***", cap.get(4))
        # sys.exit(1)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # fourcc = -1
        out = cv2.VideoWriter(out_path + 'out2.avi', fourcc, 10, (1152, 648))
        while True:
            t1 = cv2.getTickCount()
            ret, frame = cap.read()
            print("old_shape: ", frame.shape)
            frame = cv2.resize(frame, (int(frame.shape[1] * 0.6), int(frame.shape[0] * 0.6)),
                               interpolation=cv2.INTER_AREA)
            print("new_shape: ", frame.shape)
            # sys.exit(1)
            if ret == True:
                boxes_c, landmarks = mtcnn_detector.detect(frame)
                t2 = cv2.getTickCount()
                t = (t2 - t1) / cv2.getTickFrequency()
                fps = 1.0 / t
                print("fps: ", fps)
                for i in range(boxes_c.shape[0]):
                    bbox = boxes_c[i, :4]
                    score = boxes_c[i, 4]
                    corpbbox = [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])]

                    # 画人脸框
                    cv2.rectangle(frame, (corpbbox[0], corpbbox[1]),
                                  (corpbbox[2], corpbbox[3]), (255, 0, 0), 1)
                    # 画置信度
                    cv2.putText(frame, '{:.2f}'.format(score),
                                (corpbbox[0], corpbbox[1] - 2),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 0, 255), 2)
                    # 画fps值
                cv2.putText(frame, '{:.4f}'.format(t) + " " + '{:.3f}'.format(fps), (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                # 画关键点
                for i in range(landmarks.shape[0]):
                    for j in range(len(landmarks[i]) // 2):
                        cv2.circle(frame, (int(landmarks[i][2 * j]), int(int(landmarks[i][2 * j + 1]))), 2, (0, 0, 255))
                a = out.write(frame)
                cv2.imshow("result", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
        cap.release()
        out.release()
        cv2.destroyAllWindows

if __name__ == '__main__':
    test_PNet = 'PNet'
    test_RNet = 'RNet'
    test_ONet = 'ONet'
    test_mtcnn(test_PNet)
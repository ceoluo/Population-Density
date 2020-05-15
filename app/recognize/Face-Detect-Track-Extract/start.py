import argparse
import os
from time import time

import cv2
import numpy as np
import requests

from config import type_code, area_id, post_scene_url
from lib.face_utils import judge_side_face
from lib.utils import Logger, mkdir
from sort.sort import Sort
from mtcnn.train import config
from mtcnn.train.model import P_Net, R_Net, O_Net
from mtcnn.detection.fcn_detector import FcnDetector
from mtcnn.detection.detector import Detector
from mtcnn.run_mtcnn import run_mtcnn
from mtcnn.detection.MtcnnDetector import MtcnnDetector

logger = Logger()

test_mode = config.test_mode
thresh = config.thresh
min_face_size = config.min_face
stride = config.stride
detectors = [None, None, None]
# 模型放置位置
cwd_path = os.path.dirname(os.path.abspath(__file__))
model_path = [os.path.join(cwd_path, 'mtcnn/model/PNet/'), os.path.join(cwd_path, 'mtcnn/model/RNet/'),
              os.path.join(cwd_path, 'mtcnn/model/ONet')]
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

def main():
    # 参数设置
    global colours, img_size
    args = parse_args()
    videos_dir = args.videos_dir
    output_path = args.output_path
    no_display = args.no_display
    detect_interval = args.detect_interval  # you need to keep a balance between performance and fluency
    margin = args.margin  # if the face is big in your video ,you can set it bigger for tracking easiler
    scale_rate = args.scale_rate  # if set it smaller will make input frames smaller
    show_rate = args.show_rate  # if set it smaller will dispaly smaller frames
    face_score_threshold = args.face_score_threshold
    # # 创建输出目录
    # mkdir(output_path)
    # for display
    if not no_display:
        colours = np.random.rand(32, 3)

    # 初始化SORT追踪器
    tracker = Sort()

    logger.info('开始追踪人脸并且提取......')
    for filename in os.listdir(videos_dir):
        logger.info('所需要检测并追踪人脸的文件:{}'.format(filename))
    for filename in os.listdir(videos_dir):
        suffix = filename.split('.')[1]
        if suffix != 'mp4' and suffix != 'avi':  # 可以设置过滤不同的文件格式
            continue
        video_name = os.path.join(videos_dir, filename)
        logger.info('当前检测的视频文件:{}'.format(video_name))
        # 创建视频帧扑捉器，参数为文件路径或者0代表本地摄像头
        cam = cv2.VideoCapture(video_name)
        ret, frame = cam.read()
        # 创建视频保存器
        # size = (frame.shape[1], frame.shape[0])
        # video_writer = cv2.VideoWriter("output/minisize_40_07.avi", cv2.VideoWriter_fourcc(*'DIVX'), 24, size)
        # 记录已经读取到的帧数
        c = 0
        while ret:  # 循环读取整个视频文件的帧
            final_faces = []
            addtional_attribute_list = []
            # ret表示有没有读取到帧true\false
            ret, frame = cam.read()
            if not ret:
                logger.warning("ret false,没有读取到任何帧！")
                break
            if frame is None:
                logger.warning("frame drop，读取到的帧为空！")
                break
            # cv2.resize(src, dsize, dst=None, fx=None, fy=None, interpolation=None)
            # scr: 原图
            # dsize：输出图像尺寸
            # fx: 沿水平轴的比例因子
            # fy: 沿垂直轴的比例因子
            # interpolation：插值方法
            frame = cv2.resize(frame, (0, 0), fx=scale_rate, fy=scale_rate)
            # 将读取到的帧转换为rgb色彩空间
            # r_g_b_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 每隔detect_interval个帧检测跟踪一次
            faces, points = None, None
            if c % detect_interval == 0:
                img_size = np.asarray(frame.shape)[0:2]
                # mtcnn开始检测的时间戳，用于计时
                mtcnn_starttime = time()
                # 使用MTCNN实施检测，返回检测到的所有可能为face的(x1,y1,x2,y2,score)和对应的landmark
                # faces, points = detect_face.detect_face(r_g_b_frame, minsize, pnet, rnet, onet, threshold,
                #                                         factor)
                faces, points = run_mtcnn(frame, mtcnn_detector)
                points = points[np.newaxis, :]
                logger.info("MTCNN检测人脸花费时间: {} s".format(round(time() - mtcnn_starttime, 3)))
                face_sums = faces.shape[0]

                # 如果检测到的脸大于0，将每张脸剪切出来，并进行侧脸评判
                if face_sums > 0:
                    face_list = []
                    for i, item in enumerate(faces):
                        score = round(faces[i, 4], 6)
                        if score > face_score_threshold:
                            det = np.squeeze(faces[i, 0:4])

                            # face rectangle
                            det[0] = np.maximum(det[0] - margin, 0)
                            det[1] = np.maximum(det[1] - margin, 0)
                            det[2] = np.minimum(det[2] + margin, img_size[1])
                            det[3] = np.minimum(det[3] + margin, img_size[0])
                            face_list.append(item)

                            # face cropped
                            bb = np.array(det, dtype=np.int32)

                            # use 5 face landmarks  to judge the face is front or side
                            # squeeze_points = np.squeeze(points[:, i])
                            # tolist = squeeze_points.tolist()
                            # facial_landmarks = []
                            # for j in range(5):
                            #     item = [tolist[j], tolist[(j + 5)]]
                            #     facial_landmarks.append(item)

                            cropped = frame[bb[1]:bb[3], bb[0]:bb[2], :].copy()
                            # 计算五个标定点的高宽比例，高均方差，宽均方差
                            # dist_rate, high_ratio_variance, width_rate = judge_side_face(
                            #     np.array(facial_landmarks))
                            # 整个视频中脸部附加属性addtional_attribute
                            # item_list = [cropped, score, dist_rate, high_ratio_variance, width_rate]
                            item_list = [cropped, score]
                            addtional_attribute_list.append(item_list)
                    # 获取的每帧的face的score大于阈值的face
                    final_faces = np.array(face_list)

            trackers = tracker.update(final_faces, img_size, addtional_attribute_list, detect_interval)
            if faces is not None:
                # 每隔30帧上报一次
                if c % 1 == 0:
                    for i in range(faces.shape[0]):
                        bbox = faces[i, :4]
                        score = faces[i, 4]
                        corpbbox = [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])]
                        # 画人脸框
                        cv2.rectangle(frame, (corpbbox[0], corpbbox[1]),
                                      (corpbbox[2], corpbbox[3]), (255, 0, 0), 1)
                        # 判别为人脸的置信度
                        cv2.putText(frame, '{:.2f}'.format(score),
                                    (corpbbox[0], corpbbox[1] - 2),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    # 画关键点
                    if args.face_landmarks:
                        for i in range(points[0].shape[0]):
                            for j in range(len(points[0][i]) // 2):
                                cv2.circle(frame, (int(points[0][i][2 * j]), int(int(points[0][i][2 * j + 1]))), 2,
                                           (0, 0, 255))
                    # cv2.imshow('im', frame)
                    # cv2.waitKey(0)

                    for d in trackers:
                        if not no_display:
                            d = d.astype(np.int32)
                            cv2.rectangle(frame, (d[0], d[1]), (d[2], d[3]), colours[d[4] % 32, :] * 255, 3)
                            if final_faces != []:
                                cv2.putText(frame, 'ID : %d' % (d[4]), (d[0] - 10, d[1] - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            0.75,
                                            colours[d[4] % 32, :] * 255, 2)
                                cv2.putText(frame, 'DETECTOR', (5, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                                            (1, 1, 1), 2)
                            else:
                                cv2.putText(frame, 'ID : %d' % (d[4]), (d[0] - 10, d[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                            0.75,
                                            colours[d[4] % 32, :] * 255, 2)
                    # video_writer.write(frame)
                    data = {"type_code": type_code, "area_id": area_id}
                    file = {"scene_img": ("scene_img.jpg", cv2.imencode(".jpg", frame)[1].tobytes(), "image/jpg")}
                    res = requests.post(url=post_scene_url, files=file, data=data)
                    logger.info("检测场景发送到服务器，响应码：{}".format(res))

                    if not no_display:
                        frame = cv2.resize(frame, (0, 0), fx=show_rate, fy=show_rate)
                        cv2.imshow("Frame", frame)
                        # cv2.imwrite("frame.jpg",frame)
                        cv2.waitKey(1)

            c += 1

            # # 每隔30帧上报一次
            # if c % 30 == 0:
            #     for i in range(faces.shape[0]):
            #         bbox = faces[i, :4]
            #         score = faces[i, 4]
            #         corpbbox = [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])]
            #         # 画人脸框
            #         cv2.rectangle(frame, (corpbbox[0], corpbbox[1]),
            #                       (corpbbox[2], corpbbox[3]), (255, 0, 0), 1)
            #         # 判别为人脸的置信度
            #         cv2.putText(frame, '{:.2f}'.format(score),
            #                     (corpbbox[0], corpbbox[1] - 2),
            #                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            #     # 画关键点
            #     if args.face_landmarks:
            #         for i in range(points[0].shape[0]):
            #             for j in range(len(points[0][i]) // 2):
            #                 cv2.circle(frame, (int(points[0][i][2 * j]), int(int(points[0][i][2 * j + 1]))), 2, (0, 0, 255))
            #     # cv2.imshow('im', frame)
            #     # cv2.waitKey(0)
            #
            #     for d in trackers:
            #         if not no_display:
            #             d = d.astype(np.int32)
            #             cv2.rectangle(frame, (d[0], d[1]), (d[2], d[3]), colours[d[4] % 32, :] * 255, 3)
            #             if final_faces != []:
            #                 cv2.putText(frame, 'ID : %d' % (d[4]), (d[0] - 10, d[1] - 10),
            #                             cv2.FONT_HERSHEY_SIMPLEX,
            #                             0.75,
            #                             colours[d[4] % 32, :] * 255, 2)
            #                 cv2.putText(frame, 'DETECTOR', (5, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
            #                             (1, 1, 1), 2)
            #             else:
            #                 cv2.putText(frame, 'ID : %d' % (d[4]), (d[0] - 10, d[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
            #                             0.75,
            #                             colours[d[4] % 32, :] * 255, 2)
            #     # video_writer.write(frame)
            #     data = {"type_code": type_code, "area_id": area_id}
            #     file = {"scene_img": ("scene_img.jpg", cv2.imencode(".jpg", frame)[1].tobytes(), "image/jpg")}
            #     res = requests.post(url=post_scene_url, files=file, data=data)
            #     logger.info("检测场景发送到服务器，响应码：{}".format(res))
            #
            #     if not no_display:
            #         frame = cv2.resize(frame, (0, 0), fx=show_rate, fy=show_rate)
            #         cv2.imshow("Frame", frame)
            #         # cv2.imwrite("frame.jpg",frame)
            #         cv2.waitKey(1)


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--videos_dir", type=str,
                        help='Path to the data directory containing aligned your face patches.', default='videos')
    parser.add_argument('--output_path', type=str,
                        help='Path to save face',
                        default='facepics')
    parser.add_argument('--detect_interval',
                        help='how many frames to make a detection',
                        type=int, default=3)#1
    parser.add_argument('--margin',
                        help='add margin for face',
                        type=int, default=5)#10
    parser.add_argument('--scale_rate',
                        help='Scale down or enlarge the original video img',
                        type=float, default=0.5)
    parser.add_argument('--show_rate',
                        help='Scale down or enlarge the imgs drawn by opencv',
                        type=float, default=1)
    parser.add_argument('--face_score_threshold',
                        help='The threshold of the extracted faces,range 0<x<=1',
                        type=float, default=0.85)# 0.85
    parser.add_argument('--face_landmarks',
                        help='Draw five face landmarks on extracted face or not ', action="store_true", default=True)
    parser.add_argument('--no_display',
                        help='Display or not', action='store_true')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()

import argparse
import os
from time import time

import align.detect_face as detect_face
import cv2
import numpy as np
import tensorflow as tf
from lib.face_utils import judge_side_face
from lib.utils import Logger, mkdir
# 获取项目根目录
from project_root_dir import project_dir,base_url,type_code,area_id,base_url
from src.sort import Sort

logger = Logger()


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
    # 创建输出目录
    mkdir(output_path)
    # for display
    if not no_display:
        colours = np.random.rand(32, 3)

    # 初始化SORT追踪器
    tracker = Sort()

    logger.info('开始追踪人脸并且提取......')
    with tf.Graph().as_default():
        with tf.Session(config=tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True),
                                              log_device_placement=False)) as sess:
            # 创建人脸检测MTCNN的三个网络
            pnet, rnet, onet = detect_face.create_mtcnn(sess, os.path.join(project_dir, "align"))
            # 设置MTCNN能检测到的最小size的脸
            minsize = 40
            # 三个网络的人脸阈值
            threshold = [0.6, 0.7, 0.7]
            # 尺度因子
            factor = 0.709  # scale factor

            for filename in os.listdir(videos_dir):
                logger.info('所需要检测并追踪人脸的文件:{}'.format(filename))
            for filename in os.listdir(videos_dir):
                suffix = filename.split('.')[1]
                if suffix != 'mp4' and suffix != 'avi': # 可以设置过滤不同的文件格式
                    continue
                video_name = os.path.join(videos_dir, filename)
                directoryname = os.path.join(output_path, filename.split('.')[0])
                logger.info('当前检测的视频文件:{}'.format(video_name))
                # 创建视频帧扑捉器，参数为文件路径或者0代表本地摄像头
                cam = cv2.VideoCapture(video_name)
                # 记录已经读取到的帧数
                c = 0
                while True: # 循环读取整个视频文件的帧
                    final_fces = []
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
                    r_g_b_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # 每隔detect_interval个帧检测跟踪一次
                    if c % detect_interval == 0:
                        img_size = np.asarray(frame.shape)[0:2]
                        # mtcnn开始检测的时间戳，用于计时
                        mtcnn_starttime = time()
                        # 使用MTCNN实施检测，返回检测到的所有可能为face的(x1,y1,x2,y2,score)和对应的landmark
                        faces, points = detect_face.detect_face(r_g_b_frame, minsize, pnet, rnet, onet, threshold,factor)
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
                                    # bounding box 距离fram左边的距离
                                    bb_left = det[0]
                                    # bounding box 距离fram上边的距离
                                    bb_top = det[1]
                                    # use 5 face landmarks  to judge the face is front or side
                                    squeeze_points = np.squeeze(points[:, i])
                                    tolist = squeeze_points.tolist()
                                    facial_landmarks = []
                                    facial_landmarks_crap = []
                                    for j in range(5):
                                        item = [tolist[j], tolist[(j + 5)]]
                                        facial_landmarks.append(item)
                                        item_crap = [tolist[j]-bb_left, tolist[(j+5)]-bb_top]
                                        facial_landmarks_crap.append(item_crap)
                                    # 为脸画出标定点
                                    if args.face_landmarks:
                                        for (x, y) in facial_landmarks:
                                            cv2.circle(frame, (int(x), int(y)), 3, (0, 255, 0), -1)
                                    # 从帧中复制出人脸
                                    cropped = frame[bb[1]:bb[3], bb[0]:bb[2], :].copy()
                                    # 计算五个标定点的高宽比例，高均方差，宽均方差
                                    dist_rate, high_ratio_variance, width_rate = judge_side_face(np.array(facial_landmarks))
                                    # 整个视频中脸部附加属性addtional_attribute (index 0:face score; index 1:0代表正脸，1代表侧脸 )
                                    item_list = [cropped, score, dist_rate, high_ratio_variance, width_rate,facial_landmarks_crap] ##### 添加参数facial_landmarks
                                    addtional_attribute_list.append(item_list)
                            # 获取的每帧的face的score大于阈值的face
                            final_faces = np.array(face_list)

                    trackers = tracker.update(final_faces, img_size, directoryname, addtional_attribute_list, detect_interval,base_url,type_code,area_id)

                    c += 1

                    for d in trackers:
                        if not no_display:
                            d = d.astype(np.int32)
                            cv2.rectangle(frame, (d[0], d[1]), (d[2], d[3]), colours[d[4] % 32, :] * 255, 3)
                            if final_faces != []:
                                cv2.putText(frame, 'ID : %d  DETECT' % (d[4]), (d[0] - 10, d[1] - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            0.75,
                                            colours[d[4] % 32, :] * 255, 2)
                                cv2.putText(frame, 'DETECTOR', (5, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                                            (1, 1, 1), 2)
                            else:
                                cv2.putText(frame, 'ID : %d' % (d[4]), (d[0] - 10, d[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                            0.75,
                                            colours[d[4] % 32, :] * 255, 2)

                    if not no_display:
                        frame = cv2.resize(frame, (0, 0), fx=show_rate, fy=show_rate)
                        cv2.imshow("Frame", frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break


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
                        type=int, default=1)
    parser.add_argument('--margin',
                        help='add margin for face',
                        type=int, default=10)
    parser.add_argument('--scale_rate',
                        help='Scale down or enlarge the original video img',
                        type=float, default=0.7)
    parser.add_argument('--show_rate',
                        help='Scale down or enlarge the imgs drawn by opencv',
                        type=float, default=1)
    parser.add_argument('--face_score_threshold',
                        help='The threshold of the extracted faces,range 0<x<=1',
                        type=float, default=0.85)
    parser.add_argument('--face_landmarks',
                        help='Draw five face landmarks on extracted face or not ', action="store_false",default=False)
    parser.add_argument('--no_display',
                        help='Display or not', action='store_true')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()

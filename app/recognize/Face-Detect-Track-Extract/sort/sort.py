from __future__ import print_function

import lib.utils as utils
import numpy as np
from sort.data_association import associate_detections_to_trackers
from sort.kalman_tracker import KalmanBoxTracker

logger = utils.Logger("MOT")


class Sort:
    def __init__(self, max_age=1, min_hits=3):
        """
        Sets key parameters for SORT
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.trackers = []
        self.frame_count = 0

    def update(self, dets, img_size, addtional_attribute_list, predict_num):
        """
        Params:
        dets - 是所有检测物的numpy array, 为[[x1,y1,x2,y2,score],...]形式.
        Requires: 每一检测的帧必须调用这个方法一次，即时没有检测到任何目标.
        Returns：返回一个类似形式的numpy array,每一行的最后一个元素是目标的id.[[x1,y1,x2,y2,id],...]

        NOTE:as in practical realtime MOT, the detector doesn't run on every single frame
        """
        self.frame_count += 1
        # 从已有的追踪器中预测位置.
        trks = np.zeros((len(self.trackers), 5))
        to_del = []
        ret = []
        for t, trk in enumerate(trks):
            pos = self.trackers[t].predict()  # kalman predict ,very fast ,<1ms
            trk[:] = [pos[0], pos[1], pos[2], pos[3], 0]
            if np.any(np.isnan(pos)):
                to_del.append(t)
        trks = np.ma.compress_rows(np.ma.masked_invalid(trks))
        for t in reversed(to_del):
            self.trackers.pop(t)
        if dets != []:
            # 使用匈牙利算法解决数据关联的问题
            matched, unmatched_dets, unmatched_trks = associate_detections_to_trackers(dets, trks)

            # update matched trackers with assigned detections
            for t, trk in enumerate(self.trackers):
                if t not in unmatched_trks:
                    d = matched[np.where(matched[:, 1] == t)[0], 0]
                    trk.update(dets[d, :][0])
                    try:
                        trk.face_addtional_attribute.append(addtional_attribute_list[d[0]])
                    except Exception as e:
                        pass
            # create and initialise new tr ackers for unmatched detections
            # 为没有匹配的检测物创建和初始化一个新的追踪器
            for i in unmatched_dets:
                # 使用卡尔曼滤波解决动作预测的问题
                trk = KalmanBoxTracker(dets[i, :])
                trk.face_addtional_attribute.append(addtional_attribute_list[i])
                # 调用接口传送
                logger.info("new Tracker: {0}".format(trk.id + 1)) # trk.id从零开始计数
                utils.save_to_file(trk)
                # 将新创建的追踪器添加到所有追踪器集合中
                self.trackers.append(trk)

        i = len(self.trackers)
        for trk in reversed(self.trackers):
            if dets == []:
                trk.update([])
            d = trk.get_state()
            if (trk.time_since_update < 1) and (trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits):
                ret.append(np.concatenate((d, [trk.id + 1])).reshape(1, -1))  # +1 as MOT benchmark requires positive
            i -= 1
            # remove dead tracklet
            if trk.time_since_update >= self.max_age or trk.predict_num >= predict_num or d[2] < 0 or d[3] < 0 or d[0] > img_size[1] or d[1] > img_size[0]:
                logger.info('remove tracker: {0}'.format(trk.id + 1))
                self.trackers.pop(i)
        if len(ret) > 0:
            return np.concatenate(ret)
        return np.empty((0, 5))

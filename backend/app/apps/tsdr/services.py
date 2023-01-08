from PIL import ImageShow
import cv2
import numpy as np
import logging
import os
import time
from datetime import datetime

from app.apps.tsdr.tsdr_result import TsdrResult

import yolox.tools.demo as tsd_demo
from yolox.tools.infer_result import InferResult as TsdResult
import yolox.exp.example.custom.yolox_s_gtsdb as gtsdb
import tsrresnet.tools.inference as tsr_infer
from tsrresnet.tools.infer_result import InferResult as TsrResult
from tsrresnet.tools.infer_result import InferResultList as TsrResultList


logger = logging.getLogger('backend')


def get_tsd_predictor():
    logger.info('Initializing yoloX pytorch model for traffic sign detection')
    predictor = tsd_demo.PredictorBuilder(
        exp=gtsdb.Exp(),
        options='image '
                '-n yolox-s '
                '-c resources/gtsdb_best_ckpt.pth '
                '--device gpu '
                '--tsize 800 '
                '--conf 0.8'
    ).build()
    predictor.warmup(2)
    logger.info('Initialization of yoloX pytorch model complete')
    return predictor


predictor = get_tsd_predictor()


def save_result(result_image):
    save_folder = 'storage/tsd'
    os.makedirs(save_folder, exist_ok=True)
    time_now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]
    save_file_name = save_folder + '/' + time_now + '.jpg'
    logger.info("Saving detection result in {}".format(save_file_name))
    cv2.imwrite(save_file_name, result_image)
    return save_file_name


def tsd(image):
    tsd_result = predictor.inference(image)
    return tsd_result


def tsd_file(image_file):
    image = cv2.imdecode(np.frombuffer(image_file.file.read(), np.uint8), cv2.IMREAD_UNCHANGED)

    outputs, img_info = predictor.inference(image)
    result_image = predictor.visual(outputs[0], img_info, predictor.confthre)
    save_file_name = save_result(result_image)

    # img_encode = bytearray(cv2.imencode('.png', result_image)[1])
    # image_file = cv2.imread(save_file_name)
    logger.info("Filename: " + save_file_name)
    image_file = open("storage/tsd/2022_07_18_19_08_17_438.jpg", mode='rb').read()
    return image_file


def tsr(image):
    tsr_result = tsr_infer.predict_class(image, confthre=0.8)
    return tsr_result


def tsdr(image):
    start_time = time.process_time()
    tsd_result = tsd(image)
    boxed_images = tsd_result.get_boxed_images()
    tsr_result_list = TsrResultList()
    for box in boxed_images:
        tsr_result = tsr(box)
        tsr_result_list.append(tsr_result)
    result_image = TsdrResult(tsd_result, tsr_result_list).visual()
    #save_result(result_image)
    end_time = time.process_time()
    tsdr_infer_time = end_time - start_time
    logger.info(f"Identified Classes ({tsr_result_list.infer_sum():.4f}s): {str(tsr_result_list)}")
    logger.info(f"Overall infer time: {tsdr_infer_time:.4f}s")
    return tsr_result_list.get_class_ids(), result_image


class ActiveTrafficSigns:
    MIN_COUNT_NEEDED = 3
    ICONS_FOLDER = "resources/images/classes"
    ICON_SIZE_PRCT = 0.05

    def __init__(self):
        self.count_dic = {}

    def update(self, image):
        detected_classes, result_image = tsdr(image)
        combined_set = set(self.count_dic.keys())
        combined_set.update(set(detected_classes))
        # increment counter for every time a detected class is seen subsequently
        # reset counter if class is not detected anymore
        for class_id in combined_set:
            if class_id in detected_classes:
                self.push(class_id)
            else:
                self.pop(class_id)
        logger.info(f"Active classes: {self.__str__()}")
        return self.visual(result_image)

    def push(self, class_id):
        if class_id in self.count_dic:
            self.count_dic[class_id] += 1
        else:
            self.count_dic[class_id] = 1

    def pop(self, class_id):
        self.count_dic.pop(class_id)

    def get_active_signs(self):
        active_classes = []
        for class_id in self.count_dic:
            if self.count_dic[class_id] >= ActiveTrafficSigns.MIN_COUNT_NEEDED:
                if class_id == tsr_infer.NUM_CLASSES or class_id == tsr_infer.NUM_CLASSES-1:
                    pass
                else:
                    active_classes.append(class_id)
        return active_classes

    def __str__(self):
        str_list = []
        for class_id in self.get_active_signs():
            str_list.append(str(TsrResult.CLASS_NAMES[class_id]))
        return ', '.join(str_list)

    def visual(self, image):
        active_signs = self.get_active_signs()
        for i in range(len(active_signs)):
            class_id = active_signs[i]
            icon = cv2.imread(f"{ActiveTrafficSigns.ICONS_FOLDER}/{class_id}.png", cv2.IMREAD_UNCHANGED)
            icon = self.resize_icon(icon, image)
            x_offset, y_offset = self.calculate_offset(i, len(active_signs), image)
            image = self.overlay_icon(icon, image, x_offset, y_offset)
        # TODO

        return image

    def resize_icon(self, icon, image):
        # calculate appropriate dimensions for sign icon
        new_width = int(image.shape[1] * ActiveTrafficSigns.ICON_SIZE_PRCT)
        new_height = int(icon.shape[0] * new_width / icon.shape[1])
        dim = (new_width, new_height)
        # resize sign icon
        sign_img = cv2.resize(icon, dim)
        return sign_img

    def calculate_offset(self, icon_index, num_icons, image):
        prct = ActiveTrafficSigns.ICON_SIZE_PRCT
        dist_between_icons = prct * 0.1

        x_offset_BASE = 0.5
        x_offset_BASE = x_offset_BASE - prct * num_icons/2.0
        x_offset_BASE = x_offset_BASE - dist_between_icons * (num_icons-1)/2.0
        x_offset = x_offset_BASE + (prct+dist_between_icons) * icon_index
        x_offset = int(image.shape[1] * x_offset)

        y_offset = int(image.shape[0] * (1.0 - 2*prct))

        return x_offset, y_offset

    # source: https://gist.github.com/uchidama/6d51e8d4b740b4cac14855a55b9c65ef
    def overlay_icon(self, img_dst, bg_img, x_offset, y_offset):
        y1, y2 = y_offset, y_offset + img_dst.shape[0]
        x1, x2 = x_offset, x_offset + img_dst.shape[1]

        alpha_s = img_dst[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s

        for c in range(0, 3):
            bg_img[y1:y2, x1:x2, c] = (alpha_s * img_dst[:, :, c] + alpha_l * bg_img[y1:y2, x1:x2, c])

        return bg_img





from PIL import ImageShow
import cv2
import numpy as np
import logging
import os
import time
from datetime import datetime

import yolox.tools.demo as tsd_demo
import yolox.exp.example.custom.yolox_s_gtsdb as gtsdb
import tsrresnet.tools.inference as tsr_infer
import tsrresnet.tools.infer_result as tsr_result

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
                '--conf 0.3'
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
    outputs, img_info = predictor.inference(image)
    result_image = predictor.visual(outputs[0], img_info, predictor.confthre)
    boxes = predictor.boxes(outputs[0], img_info, predictor.confthre)

    return boxes, result_image


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
    class_str = tsr_infer.predict_class(image)
    return class_str


def tsdr(image):
    boxes, tsd_image = tsd(image)
    infer_result_list = tsr_result.InferResultList()
    start_time = time.time()
    for box in boxes:
        infer_result = tsr(box)
        infer_result_list.append(infer_result)
    end_time = time.time()
    tsdr_infer_time = end_time - start_time
    logger.info(f"Identified Classes ({infer_result_list.infer_sum():.4f}s): {str(infer_result_list)}")
    logger.info(f"TSDR (Detection+Recognition) infer time: {tsdr_infer_time:.4f}s")

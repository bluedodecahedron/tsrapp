import yolox.tools.demo as demo
import yolox.exp.example.custom.yolox_s_gtsdb as gtsdb
from PIL import ImageShow
import cv2
import numpy as np
import logging
import os
import time


logger = logging.getLogger('backend')


def get_tsd_predictor():
    logger.info('Initializing yoloX pytorch model for traffic sign detection')
    predictor = demo.PredictorBuilder(
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
    save_file_name = os.path.join(save_folder, time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '.jpg')
    logger.info("Saving detection result in {}".format(save_file_name))
    cv2.imwrite(save_file_name, result_image)


def tsd(image_file):
    image = cv2.imdecode(np.frombuffer(image_file.file.read(), np.uint8), cv2.IMREAD_UNCHANGED)

    outputs, img_info = predictor.inference(image)
    result_image = predictor.visual(outputs[0], img_info, predictor.confthre)
    save_result(result_image)
    # cv2.imshow('Image', result_image)
    # cv2.waitKey(0)

    return 0

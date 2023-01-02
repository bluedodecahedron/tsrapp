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
                '--conf 0.5'
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
    tsr_result = tsr_infer.predict_class(image, confthre=0.5)
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

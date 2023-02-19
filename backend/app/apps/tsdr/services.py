from PIL import ImageShow
import cv2
import numpy as np
import logging
import os
import time
import signal
from datetime import datetime

from app.apps.tsdr.tsdr_result import TsdrResult

import yolox.tools.demo as tsd_demo
from yolox.tools.infer_result import InferResult as TsdResult
import yolox.exp.example.custom.yolox_s_gtsdb as gtsdb
import tsrresnet.tools.inference as tsr_inference
from tsrresnet.tools.infer_result import InferResult as TsrResult


logger = logging.getLogger('backend')

ICONS_FOLDER = "resources/images/classes"
TSD_MODEL = 'resources/gtsdb_best_ckpt.pth'
TSR_MODEL = 'resources/model.pth'
CLASS_NAMES = 'resources/signnames.csv'
TSD_CONFIDENCE = 0.75
TSR_CONFIDENCE = 0.8
TSR_MAX_WORKERS = 5

VIDEO_OUTPUT_ROOT = 'storage/videos'
VIDEO_FPS = 15.0
VIDEO_MAX_SECONDS = 1 * 60 * 60  # 1 hour in seconds


def build_tsd_predictor():
    logger.info('Initializing yoloX pytorch model for traffic sign detection')
    predictor = tsd_demo.PredictorBuilder(
        exp=gtsdb.Exp(),
        options='image '
                '-n yolox-s '
                f'-c {TSD_MODEL} '
                '--device gpu '
                '--tsize 800 '
                f'--conf {TSD_CONFIDENCE}'
    ).build()
    predictor.warmup(2)
    logger.info('Initialization of yoloX pytorch model complete')
    return predictor


def build_tsr_predictor():
    logger.info('Initializing resnet pytorch model for traffic sign classification')
    predictor = tsr_inference.Predictor(
        model_path=TSR_MODEL,
        classes_path=CLASS_NAMES,
        device='cuda',
        max_workers=TSR_MAX_WORKERS,
        confthre=TSR_CONFIDENCE
    )
    return predictor


def build_tsr_result():
    result = TsrResult(CLASS_NAMES)
    return result


tsd_predictor = build_tsd_predictor()
tsr_predictor = build_tsr_predictor()
tsr_infer_result = build_tsr_result()


def load_icons():
    icons = []
    for i in range(len(tsr_infer_result.class_names)-2):
        icon = cv2.imread(f"{ICONS_FOLDER}/{i}.png", cv2.IMREAD_UNCHANGED)
        icons.append(icon)
    return icons


icon_list = load_icons()


def save_result(result_image):
    save_folder = 'storage/tsd'
    os.makedirs(save_folder, exist_ok=True)
    time_now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]
    save_file_name = save_folder + '/' + time_now + '.jpg'
    logger.info("Saving detection result in {}".format(save_file_name))
    cv2.imwrite(save_file_name, result_image)
    return save_file_name


def tsd(image):
    result = tsd_predictor.inference(image)
    return result


def tsd_file(image_file):
    image = cv2.imdecode(np.frombuffer(image_file.file.read(), np.uint8), cv2.IMREAD_UNCHANGED)

    outputs, img_info = tsd_predictor.inference(image)
    result_image = tsd_predictor.visual(outputs[0], img_info, tsd_predictor.confthre)
    save_file_name = save_result(result_image)

    # img_encode = bytearray(cv2.imencode('.png', result_image)[1])
    # image_file = cv2.imread(save_file_name)
    logger.info("Filename: " + save_file_name)
    image_file = open("storage/tsd/2022_07_18_19_08_17_438.jpg", mode='rb').read()
    return image_file


def tsr(images):
    result_list = tsr_predictor.multi_inference_gpu(images)
    return result_list


def tsdr(image):
    start_time = time.perf_counter()
    tsd_result = tsd(image)
    boxed_images = tsd_result.boxed_images
    logger.info("Tsd took: {:.4f}s".format(time.perf_counter() - start_time))
    tsr_result_list = tsr(boxed_images)

    result_image = TsdrResult(tsd_result, tsr_result_list).visual()
    # save_result(result_image)
    logger.info(f"Identified Classes ({len(tsr_result_list.list)}, {tsr_result_list.multi_time:.4f}s): {str(tsr_result_list)}")
    logger.info(f"Overall infer time: {time.perf_counter()-start_time:.4f}s")
    return tsr_result_list.get_class_ids(), result_image


class TsdrState:
    def __init__(self, video_fps=VIDEO_FPS):
        time_now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]
        self.active_traffic_signs = ActiveTrafficSigns(logfile_name=time_now, video_fps=video_fps)
        self.video_builder = VideoBuilder(file_name=time_now, video_fps=video_fps)

    def update(self, image):
        result_image = self.active_traffic_signs.update(image)
        self.video_builder.update(result_image)
        return result_image

    def release(self, *args):
        self.active_traffic_signs.release()
        self.video_builder.release()


class VideoBuilder:
    def __init__(self, file_name, video_fps=VIDEO_FPS):
        self.videoOutput = VIDEO_OUTPUT_ROOT + f'/{file_name}.mp4'
        self.videoFps = video_fps
        self.video_max_frames = VIDEO_MAX_SECONDS * self.videoFps
        self.frameSize = None
        self.videoWriter = None
        self.frameCounter = 0

    def update(self, image):
        start_time = time.perf_counter()
        self.add_frame(image)
        logger.info(f"Video update time: {time.perf_counter()-start_time:.4f}s")

    def add_frame(self, frame):
        if self.frameCounter == self.video_max_frames:
            self.release()

        if self.videoWriter is None:
            self.create_writer(frame)

        frame = cv2.resize(frame, self.frameSize)
        self.videoWriter.write(frame)
        self.frameCounter += 1

    def create_writer(self, frame):
        self.create_root()
        height, width, _ = frame.shape
        self.frameSize = (width, height)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Be sure to use lower case
        self.videoWriter = cv2.VideoWriter(self.videoOutput, fourcc, self.videoFps, self.frameSize)

    def create_root(self):
        if not os.path.exists(VIDEO_OUTPUT_ROOT):
            os.makedirs(VIDEO_OUTPUT_ROOT)

    def release(self):
        if self.videoWriter is not None:
            logger.info(f"Releasing video file {self.videoOutput}")
            self.videoWriter.release()
            self.videoWriter = None


class ActiveTrafficSigns:
    # Number of frames in a row that a traffic sign needs to be detected to count as active
    MIN_COUNT_NEEDED = 3
    # Number of seconds a traffic sign has to be inactive before it gets logged again
    MIN_DELAY_LOG = 2
    # Icon width in percent of input image
    ICON_SIZE_PRCT = 0.1
    # Do not count the last x classes in class_names as active
    CLASSES_TO_IGNORE = 11

    def __init__(self, logfile_name, video_fps=VIDEO_FPS):
        self.count_dic = {}
        self.frame_dic = {}
        self.video_fps = video_fps
        self.frameCount = 0
        self.active_log = []
        self.logfile_path = f'{VIDEO_OUTPUT_ROOT}/{logfile_name}.txt'
        self.log_file = open(self.logfile_path, 'a')

    def update(self, image):
        self.frameCount += 1
        start_time = time.perf_counter()
        detected_classes, result_image = tsdr(image)
        combined_set = set(self.count_dic.keys())
        combined_set.update(set(detected_classes))
        # increment counter for every time a detected class is seen subsequently
        # reset counter if class is not detected anymore
        for class_id in combined_set:
            if class_id in detected_classes:
                self.append(class_id)
            else:
                self.remove(class_id)
        logger.info(f"Active classes: {self.__str__()}")
        result_image = self.visual(result_image)
        logger.info(f"Active update time: {time.perf_counter() - start_time:.4f}s")
        return result_image

    def append(self, class_id):
        if class_id in self.count_dic:
            self.count_dic[class_id] += 1
        else:
            self.count_dic[class_id] = 1

    def remove(self, class_id):
        self.count_dic.pop(class_id)

    def get_active_signs(self):
        active_classes = []
        for class_id in self.count_dic:
            if self.count_dic[class_id] >= self.MIN_COUNT_NEEDED:
                if class_id >= len(tsr_infer_result.class_names)-self.CLASSES_TO_IGNORE:
                    # traffic sign is ignored
                    pass
                else:
                    active_classes.append(class_id)
                    self.log(class_id)
                    self.frame_dic[class_id] = self.frameCount
        return active_classes

    def log(self, class_id):
        is_delay = True
        if class_id in self.frame_dic:
            frames_diff = self.frameCount - self.frame_dic[class_id]
            frames_needed = self.video_fps * self.MIN_DELAY_LOG
            is_delay = frames_diff > frames_needed
        is_new = self.count_dic[class_id] == self.MIN_COUNT_NEEDED
        if is_new and is_delay:
            time_passed = self.frameCount / self.video_fps
            class_name = str(tsr_infer_result.class_names[class_id])
            self.log_file.write(f'{self.to_hhmmss(time_passed)} {class_name}\n')
            # self.active_log.append(f'{self.to_hhmmss(time_passed)} {class_name}')

    def release(self):
        logger.info(f'Releasing log file {self.logfile_path}')
        self.log_file.close()

    def __str__(self):
        str_list = []
        for class_id in self.get_active_signs():
            str_list.append(str(tsr_infer_result.class_names[class_id]))
        return ', '.join(str_list)

    def visual(self, image):
        active_signs = self.get_active_signs()
        for i in range(len(active_signs)):
            class_id = active_signs[i]
            icon = self.resize_icon(icon_list[class_id], image)
            x_offset, y_offset = self.calculate_offset(i, len(active_signs), image)
            image = self.overlay_icon(icon, image, x_offset, y_offset)

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

        y_offset = int(image.shape[0] * (0.7 - 0.5*prct))

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

    def to_hhmmss(self, seconds):
        hours = seconds // (60 * 60)
        seconds %= (60 * 60)
        minutes = seconds // 60
        seconds %= 60
        return "%02i:%02i:%02i" % (hours, minutes, seconds)






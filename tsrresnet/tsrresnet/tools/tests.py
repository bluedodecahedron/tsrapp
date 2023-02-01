from unittest import TestCase
import inference
import glob
import time
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed

all_images = glob.glob('../../input/GTSRB_Final_Test_Images/GTSRB/Final_Test/Images/*.ppm')
sub_images = glob.glob('../../input/GTSRB_Final_Training_Images/GTSRB/Final_Training/Images/00001/*.ppm')
asset_images = glob.glob('../../assets/*.jpg')
images = all_images


class TestInference(TestCase):
    def setUp(self) -> None:
        self.predictor = inference.Predictor(
            '../../outputs/model.pth',
            '../../input/signnames.csv',
            max_workers=5,
            confthre=0.95
        )

    def tsr(self, image):
        tsr_result = self.predictor.inference(image)
        return tsr_result

    def multi_tsr(self, image):
        tsr_result_list = self.predictor.multi_inference(image)
        return tsr_result_list

    def test_inference(self):
        frame_counter = 0
        infer_time = 0.0
        for i, image_path in enumerate(sub_images):
            image = cv2.imread(image_path)
            start_time = time.perf_counter()
            self.tsr(image)
            end_time = time.perf_counter()
            print(f"Image {i} took {end_time-start_time}s")
            infer_time += end_time-start_time
            frame_counter += 1
        fps = frame_counter / infer_time
        print(f"FPS: {fps:.3f}")

    def test_multi_inference(self):
        use_images = sub_images
        image_batch = []
        for i, image_path in enumerate(use_images):
            image = cv2.imread(image_path)
            image_batch.append(image)
            if (i % 5 == 0) or (i == len(use_images)-1):
                result_list = self.multi_tsr(image_batch)
                print(f"Identified Classes ({result_list.multi_time:.4f}s): {str(result_list)}")
                image_batch = []
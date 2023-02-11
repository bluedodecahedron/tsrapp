from unittest import TestCase
import inference
import glob
import time
import cv2
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from train.datasets import get_datasets, get_data_loaders
import albumentations as A

all_images = glob.glob('../../input/GTSRB_Final_Test_Images/GTSRB/Final_Test/Images/*.ppm')
sub_images = glob.glob('../../input/GTSRB_Final_Training_Images/GTSRB/Final_Training/Images/00001/*.ppm')
asset_images = glob.glob('../../assets/*.jpg')
images_glob = all_images


class TestInference(TestCase):
    def setUp(self) -> None:
        self.predictor = inference.Predictor(
            '../../outputs/models/model.pth',
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


class TesTAugmentations(TestCase):
    ROOT_DIR = '../../input/GTSRB_Final_Training_Images/GTSRB/Final_Training/Images'

    def test_mixup(self):
        dataset_train, dataset_valid, dataset_classes = get_datasets(self.ROOT_DIR)
        train_loader, valid_loader = get_data_loaders(dataset_train, dataset_valid)
        with tqdm(enumerate(train_loader), total=len(train_loader), position=0, leave=False) as pbar:
            for i, data in pbar:
                images, labels = data
                # transform to undo normalizing
                transform = A.Compose([
                    A.Normalize(
                        mean=[-0.485/0.229, -0.456/0.224, -0.406/0.225],
                        std=[1/0.229, 1/0.224, 1/0.225],
                        max_pixel_value=1.0
                    ),
                ])
                for j in range(len(images)):
                    print(f'Label: {str(labels[j])}')
                    # convert from pytorch tensor back to numpy array
                    image = images[j].numpy().transpose(1, 2, 0)
                    image = transform(image=image)['image']
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    cv2.imshow('MixUp Image', image)
                    cv2.waitKey(0)
                    continue
        cv2.destroyAllWindows()

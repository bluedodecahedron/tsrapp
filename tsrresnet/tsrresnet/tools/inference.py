import traceback

import cv2
import torch
import albumentations as A
import time
import numpy as np

from albumentations.pytorch import ToTensorV2
from torch.nn import functional as F
from torch import topk

from tsrresnet.tools.model import build_model
from tsrresnet.tools.infer_result import InferResult

from concurrent.futures import ThreadPoolExecutor, as_completed


class Predictor:
    # Define the transforms, resize => tensor => normalize.
    transform = A.Compose([
        A.Resize(224, 224),
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
        ToTensorV2(),
    ])

    def __init__(self, model_path, classes_path, device, max_workers, confthre):
        self.device = device
        self.model = self.build_model(model_path)
        self.infer_result = InferResult(classes_path)
        self.max_workers = max_workers
        self.confthre = confthre

    def build_model(self, model_path):
        # Initialize model, switch to eval model, load trained weights.
        model = build_model(
            pretrained=False,
            fine_tune=False,
        ).to(self.device)
        model = model.eval()
        model.load_state_dict(
            torch.load(
                model_path, map_location=self.device
            )['model_state_dict']
        )
        return model

    def preprocess(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # downscale image
        img = cv2.resize(img, (60, 60))
        img = cv2.resize(img, (224, 224))
        # use some augmentations that were used during training
        # size = 4
        # kernel = np.ones((size, size), np.uint8)
        # img = cv2.erode(img, kernel, iterations=1)
        # img = cv2.GaussianBlur(img, (31, 31), 0)
        transform = A.Compose([
            A.ColorJitter(brightness=(1.0, 1.0), contrast=(1.2, 1.2), saturation=(1.2, 1.2), hue=(0.0, 0.0), p=1.0),
            # A.Emboss(alpha=(0.4, 0.4), strength=(0.4, 0.4), p=1.0),
        ])
        img = transform(image=img)['image']
        # cv2.imshow("title", img)
        # cv2.waitKey(0)
        # Apply transforms to use as model input.
        tensor = self.transform(image=img)['image']
        return tensor

    def build_result(self, probs, infer_time, q_index=0):
        # get top probability
        probs_sorted, indices = torch.sort(probs, descending=True)
        take_x = 3
        top_probs = probs_sorted[0:take_x].float()
        # Get the class indices of top k probabilities.
        classes_idx = topk(probs, take_x)[1].int().tolist()
        return self.infer_result.result(classes_idx, top_probs, infer_time, self.confthre, q_index=q_index)

    def inference(self, image, q_index=0):
        start_time = time.perf_counter()
        # Return with unknown result if image has a dimension=0
        if not all(image.shape):
            return self.infer_result.result_unknown(q_index=q_index)
        orig_image = image.copy()
        tensor = self.preprocess(image)
        # Add batch dimension.
        tensor = tensor.unsqueeze(0)
        tensor = tensor.to(self.device)
        # Forward pass through model.
        outputs = self.model(tensor)
        # Get the softmax probabilities.
        probs = F.softmax(outputs, dim=1).data.squeeze()
        end_time = time.perf_counter()
        infer_time = end_time - start_time
        return self.build_result(probs, infer_time, q_index)

    def multi_inference_cpu(self, images):
        start_time = time.perf_counter()
        executor = ThreadPoolExecutor(max_workers=self.max_workers)
        futures = []
        for i, image in enumerate(images):
            future = executor.submit(self.inference, image, i)
            futures.append(future)

        result_list = self.infer_result.result_list()
        for future in as_completed(futures):
            result = future.result()
            result_list.append(result)

        result_list.sort_by_qindex()
        end_time = time.perf_counter()
        result_list.set_multi_time(end_time-start_time)

        return result_list

    def multi_inference_gpu(self, images):
        start_time = time.perf_counter()
        tensors = []
        result_list = self.infer_result.result_list()
        if len(images) == 0:
            return result_list
        for i, image in enumerate(images):
            if not all(image.shape):
                self.infer_result.result_unknown(q_index=i)
            tensor = self.preprocess(images[i])
            tensors.append(tensor.to(self.device))
        tensors = torch.stack(tensors).to(self.device)
        # Forward pass through model.
        outputs = self.model(tensors)
        # Get the softmax probabilities.
        probs_tensor = F.softmax(outputs, dim=1).data

        end_time = time.perf_counter()
        for i, probs in enumerate(probs_tensor):
            # get top probability
            result = self.build_result(probs, end_time-start_time, q_index=i)
            result_list.append(result)

        result_list.set_multi_time(end_time - start_time)
        return result_list


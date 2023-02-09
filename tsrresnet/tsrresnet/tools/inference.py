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

# Define computation device.
device = 'cuda'


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

    def __init__(self, model_path, classes_path, max_workers, confthre):
        self.model = self.build_model(model_path)
        self.infer_result = InferResult(classes_path)
        self.max_workers = max_workers
        self.confthre = confthre

    def build_model(self, model_path):
        # Initialize model, switch to eval model, load trained weights.
        model = build_model(
            pretrained=False,
            fine_tune=False,
        ).to(device)
        model = model.eval()
        model.load_state_dict(
            torch.load(
                model_path, map_location=device
            )['model_state_dict']
        )
        return model

    def inference(self, image, q_index=0):
        # Read the image.
        # image = cv2.imread(image_path)
        start_time = time.perf_counter()
        # Return with unknown result if image has a dimension=0
        if not all(image.shape):
            return self.infer_result.result_unknown(q_index=q_index)
        orig_image = image.copy()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, _ = orig_image.shape
        # Apply the image transforms.
        image_tensor = self.transform(image=image)['image']
        # Add batch dimension.
        image_tensor = image_tensor.unsqueeze(0)
        # Forward pass through model.
        outputs = self.model(image_tensor.to(device))
        # Get the softmax probabilities.
        probs = F.softmax(outputs, dim=1).data.squeeze()
        # get top probability
        probs_sorted, indices = torch.sort(probs, descending=True)
        top_prob = probs_sorted[0].float()
        # Get the class indices of top k probabilities.
        class_idx = topk(probs, 1)[1].int()
        # Set Unknown if prob below threshold
        if top_prob < self.confthre:
            # set to number of classes (=next index)
            class_idx = self.model.fc.out_features
        end_time = time.perf_counter()
        # Get the current fps.
        infer_time = end_time - start_time
        return self.infer_result.result(int(class_idx), top_prob, infer_time, self.confthre, q_index=q_index)

    def multi_inference(self, images):
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


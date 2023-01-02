import cv2
import torch
import albumentations as A
import time

from albumentations.pytorch import ToTensorV2
from torch.nn import functional as F
from torch import topk

from tsrresnet.tools.model import build_model
from tsrresnet.tools.infer_result import InferResult

# Define computation device.
device = 'cuda'

# Initialize model, switch to eval model, load trained weights.
model = build_model(
    pretrained=False,
    fine_tune=False, 
    num_classes=43
).to(device)
model = model.eval()
model.load_state_dict(
    torch.load(
        'resources/model.pth', map_location=device
    )['model_state_dict']
)

# Define the transforms, resize => tensor => normalize.
transform = A.Compose([
    A.Resize(224, 224),
    A.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
    ToTensorV2(),
    ])


def predict_class(image, confthre=0.0):
    # Read the image.
    # image = cv2.imread(image_path)
    start_time = time.process_time()
    orig_image = image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, _ = orig_image.shape
    # Apply the image transforms.
    image_tensor = transform(image=image)['image']
    # Add batch dimension.
    image_tensor = image_tensor.unsqueeze(0)
    # Forward pass through model.
    outputs = model(image_tensor.to(device))
    # Get the softmax probabilities.
    probs = F.softmax(outputs, dim=1).data.squeeze()
    # get top probability
    probs_sorted, indices = torch.sort(probs, descending=True)
    top_prob = probs_sorted[0].float()
    # Get the class indices of top k probabilities.
    class_idx = topk(probs, 1)[1].int()
    end_time = time.process_time()
    # Get the current fps.
    infer_time = end_time - start_time
    return InferResult(class_idx, top_prob, infer_time, confthre)

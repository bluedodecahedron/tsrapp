import numpy as np
import cv2
import torch
import glob as glob
import pandas as pd
import os
import albumentations as A
import time

from albumentations.pytorch import ToTensorV2
from torch.nn import functional as F
from torch import topk

from tsrmodel.tools.model import build_model

RESIZE_TO = 224
# Define computation device.
device = 'cuda'
# Class names.
sign_names_df = pd.read_csv('../input/signnames.csv')
class_names = sign_names_df.SignName.tolist()

# DataFrame for ground truth.
gt_df = pd.read_csv(
    '../input/GTSRB_Final_Test_GT/GT-final_test.csv',
    delimiter=';'
)
gt_df = gt_df.set_index('Filename', drop=True)

# Initialize model, switch to eval model, load trained weights.
model = build_model(
    pretrained=False,
    fine_tune=False
).to(device)
model = model.eval()
model.load_state_dict(
    torch.load(
        '../outputs/models/model.pth', map_location=device
    )['model_state_dict']
)


# https://github.com/zhoubolei/CAM/blob/master/pytorch_CAM.py
def returnCAM(feature_conv, weight_softmax, class_idx):
    # Generate the class activation maps upsample to 256x256.
    size_upsample = (256, 256)
    bz, nc, h, w = feature_conv.shape
    output_cam = []
    for idx in class_idx:
        cam = weight_softmax[idx].dot(feature_conv.reshape((nc, h*w)))
        cam = cam.reshape(h, w)
        cam = cam - np.min(cam)
        cam_img = cam / np.max(cam)
        cam_img = np.uint8(255 * cam_img)
        output_cam.append(cv2.resize(cam_img, size_upsample))
    return output_cam


def apply_color_map(CAMs, width, height, orig_image):
    for i, cam in enumerate(CAMs):
        heatmap = cv2.applyColorMap(cv2.resize(cam,(width, height)), cv2.COLORMAP_JET)
        result = heatmap * 0.5 + orig_image * 0.5
        result = cv2.resize(result, (RESIZE_TO, RESIZE_TO))
        return result


def visualize_and_save_map(
    result, orig_image, gt_idx=None, class_idx=None, top_prob=0, save_name=None
):
    orig_image = cv2.resize(orig_image, (256, 256))
    result = cv2.resize(result, (256, 256))
    # Put class label text on the result.
    if class_idx is not None:
        cv2.putText(
            result,
            f"Pred: {str(class_names[int(class_idx)])}", (5, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2,
            cv2.LINE_AA
        )
        cv2.putText(
            result,
            f"Prob: {top_prob*100:.2f}%", (5, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2,
            cv2.LINE_AA
        )
    if gt_idx is not None:
        cv2.putText(
            result,
            f"GT: {str(class_names[int(gt_idx)])}", (5, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2,
            cv2.LINE_AA
        )
    img_concat = cv2.hconcat([
        np.array(result, dtype=np.uint8),
        np.array(orig_image, dtype=np.uint8)
    ])
    cv2.imshow('Result', img_concat)
    cv2.waitKey(0)
    if save_name is not None:
        cv2.imwrite(f"../outputs/test_results/CAM_{save_name}.jpg", img_concat)


# Hook the feature extractor.
# https://github.com/zhoubolei/CAM/blob/master/pytorch_CAM.py
features_blobs = []
def hook_feature(module, input, output):
    features_blobs.append(output.data.cpu().numpy())
# debug variable below to check module names
modules = model._modules
# model._modules.get('layer4').register_forward_hook(hook_feature)
model._modules.get('features').register_forward_hook(hook_feature)
# Get the softmax weight.
params = list(model.parameters())
weight_softmax = np.squeeze(params[-2].data.cpu().numpy())

# Define the transforms, resize => tensor => normalize.
transform = A.Compose([
    A.Resize(RESIZE_TO, RESIZE_TO),
    A.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
    ToTensorV2(),
    ])

counter = 0
# Run for all the test images.
all_images = glob.glob('../input/GTSRB_Final_Test_Images/GTSRB/Final_Test/Images/*.ppm')
sub_images = glob.glob('../input/GTSRB_Final_Training_Images/GTSRB/Final_Training/Images/00000/*.ppm')
asset_images = glob.glob('../assets/*.jpg')
images = all_images
is_ground_truth = True
correct_count = 0
frame_count = 0 # To count total frames.
total_fps = 0 # To get the final frames per second.

# We need two lists to keep track of class-wise accuracy.
class_correct = list(0. for i in range(len(class_names)))
class_total = list(0. for i in range(len(class_names)))

for i, image_path in enumerate(images):
    if i > 100000:
        break
    # Read the image.
    image = cv2.imread(image_path)
    image = cv2.resize(image, (RESIZE_TO, RESIZE_TO))
    orig_image = image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, _ = orig_image.shape
    # Apply the image transforms.
    image_tensor = transform(image=image)['image']
    # Add batch dimension.
    image_tensor = image_tensor.unsqueeze(0)
    # Forward pass through model.
    start_time = time.time()
    outputs = model(image_tensor.to(device))
    end_time = time.time()
    # Get the softmax probabilities.
    probs = F.softmax(outputs, dim=1).data.squeeze()
    # get top probability
    top_prob = float(sorted(probs, reverse=True)[0].float())
    # Get the class indices of top k probabilities.
    class_idx = topk(probs, 1)[1].int()
    # Get the ground truth.
    image_name = image_path.split(os.path.sep)[-1]
    gt_idx = None
    if is_ground_truth:
        gt_idx = gt_df.loc[image_name].ClassId
        # Check whether correct prediction or not.
        if gt_idx == class_idx:
            correct_count += 1
            class_correct[gt_idx] += 1
        class_total[gt_idx] += 1
    # Generate class activation mapping for the top1 prediction.
    CAMs = returnCAM(features_blobs[-1], weight_softmax, class_idx)
    # File name to save the resulting CAM image with.
    save_name = f"{image_path.split('/')[-1].split('.')[0]}"
    # Show and save the results.
    result = apply_color_map(CAMs, width, height, orig_image)
    # visualize_and_save_map(result, orig_image, gt_idx, class_idx, top_prob, save_name)
    counter += 1
    print(f"Image: {counter}")
    # Get the current fps.
    fps = 1 / (end_time - start_time)
    # Add `fps` to `total_fps`.
    total_fps += fps
    # Increment frame count.
    frame_count += 1

print(f"Total number of test images: {len(all_images)}")
print(f"Total correct predictions: {correct_count}")
print(f"Accuracy: {correct_count/len(all_images)*100:.3f}")

# calculate and print the average FPS
avg_fps = total_fps / frame_count
print(f"Average FPS: {avg_fps:.3f}")

# Print the accuracy for each class.
print('\n')
for i in range(len(class_names)):
    if class_total[i] == 0:
        class_total[i] = 1
    print(f"Accuracy of class {class_names[i]}: {100 * class_correct[i] / class_total[i]}")
print('\n')

# Close all frames and video windows.
cv2.destroyAllWindows()
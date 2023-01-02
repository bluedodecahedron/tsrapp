import torch
import albumentations as A
import numpy as np
import cv2
import glob as glob
import random

from torchvision import datasets
from torch.utils.data import DataLoader, Subset
from albumentations.pytorch import ToTensorV2

# Required constants.
ROOT_DIR = '../input/GTSRB_Final_Training_Images/GTSRB/Final_Training/Images'
VALID_SPLIT = 0.1
RESIZE_TO = 224 # Image size of resize when applying transforms.
BATCH_SIZE = 64
NUM_WORKERS = 4 # Number of parallel processes for data preparation.


# Training transforms.
class TrainTransforms:
    def __init__(self, resize_to):
        self.transforms = A.Compose([
            A.Resize(224, 224),
            A.RandomBrightnessContrast(p=1),
            A.RandomGamma(p=1),
            A.CLAHE(p=1),
            A.RandomFog(),
            A.RandomRain(),
            A.ShiftScaleRotate(shift_limit=0.1, scale_limit=(-0.1, 0.6), rotate_limit=20, p=1.0),
            A.OpticalDistortion(),
            A.GridDistortion(),
            A.RandomSunFlare(flare_roi=(0, 0, 1, 0.5), angle_lower=0.5, src_radius=100, p=0.3),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
                ),
            ToTensorV2()
        ])
    
    def __call__(self, img):
        return self.transforms(image=np.array(img))['image']


# Validation transforms.
class ValidTransforms:
    def __init__(self, resize_to):
        self.transforms = A.Compose([
            A.Resize(resize_to, resize_to),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
                ),
            ToTensorV2()
        ])
    
    def __call__(self, img):
        return self.transforms(image=np.array(img))['image']


def get_datasets():
    """
    Function to prepare the Datasets.

    Returns the training and validation datasets along 
    with the class names.
    """
    dataset = datasets.ImageFolder(
        ROOT_DIR, 
        transform=(TrainTransforms(RESIZE_TO))
    )
    dataset_test = datasets.ImageFolder(
        ROOT_DIR, 
        transform=(ValidTransforms(RESIZE_TO))
    )
    dataset_size = len(dataset)

    # Calculate the validation dataset size.
    valid_size = int(VALID_SPLIT*dataset_size)
    # Radomize the data indices.
    indices = torch.randperm(len(dataset)).tolist()
    # Training and validation sets.
    dataset_train = Subset(dataset, indices[:-valid_size])
    dataset_valid = Subset(dataset_test, indices[-valid_size:])

    return dataset_train, dataset_valid, dataset.classes


def get_data_loaders(dataset_train, dataset_valid):
    """
    Prepares the training and validation data loaders.

    :param dataset_train: The training dataset.
    :param dataset_valid: The validation dataset.

    Returns the training and validation data loaders.
    """
    train_loader = DataLoader(
        dataset_train, batch_size=BATCH_SIZE, 
        shuffle=True, num_workers=NUM_WORKERS
    )
    valid_loader = DataLoader(
        dataset_valid, batch_size=BATCH_SIZE, 
        shuffle=False, num_workers=NUM_WORKERS
    )
    return train_loader, valid_loader


def visualize_transform():
    # Run for all the test images.
    all_images = glob.glob(f'{ROOT_DIR}/*/*.ppm')

    transform = A.Compose([
        A.Resize(224, 224),
        A.RandomBrightnessContrast(p=1),
        A.RandomGamma(p=1),
        A.CLAHE(p=1),
        A.RandomFog(),
        A.RandomRain(),
        A.ShiftScaleRotate(shift_limit=0.1, scale_limit=(-0.1, 0.6), rotate_limit=20, p=1.0),
        A.OpticalDistortion(),
        A.GridDistortion(),
        A.RandomSunFlare(flare_roi=(0, 0, 1, 0.5), angle_lower=0.5, src_radius=100, p=0.3)
    ])

    random.seed(42)

    for i, image_path in enumerate(all_images):
        # Read the image.
        image = cv2.imread(image_path)
        orig_image = image.copy()
        # Apply the image transforms.
        image_tensor = transform(image=image)['image']

        orig_image = cv2.resize(orig_image, (224, 224))
        img_concat = cv2.hconcat([
            np.array(orig_image, dtype=np.uint8),
            np.array(image_tensor, dtype=np.uint8)
        ])
        cv2.imshow('Result', img_concat)
        cv2.waitKey(0)

import torch
import albumentations as A
import numpy as np
import cv2
import glob as glob
import random
import PIL

from torchvision import datasets
from torch.utils.data import DataLoader, Subset
from albumentations.pytorch import ToTensorV2

# Required constants.
ROOT_DIR = '../input/GTSRB_Final_Training_Images/GTSRB/Final_Training/Images'
VALID_SPLIT = 0.1
RESIZE_TO = 224 # Image size of resize when applying transforms.
BATCH_SIZE = 64
NUM_WORKERS = 12 # Number of parallel processes for data preparation.


# Training transforms.
class TrainTransforms:
    augments = [
        # Convert to grayscale, then invert bright/dark
        A.Compose([
            A.ToGray(p=1.0),
            A.InvertImg(p=1.0)
        ], p=0.1),
        A.RandomShadow(shadow_roi=(0, 0, 1, 0.75), num_shadows_lower=1, num_shadows_upper=1, shadow_dimension=3, p=1.0),
        # Adjust brightness, contrast, hue, saturation
        A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2, p=1.0),
        # Adjust Gamma
        A.RandomGamma(gamma_limit=(80, 120), p=0.33),
        # Histogram Equalization
        A.CLAHE(clip_limit=4.0, tile_grid_size=(8, 8), p=1),
        # Simulates fog
        A.RandomFog(p=0.33),
        # Simulates rain
        A.RandomRain(p=0.25),
        # Shift(translate) Image, Scale Image, Rotate Image
        A.ShiftScaleRotate(shift_limit=0.1, scale_limit=(-0.1, 0.6), rotate_limit=15, p=1.0),
        # Distort Image by a grid
        A.GridDistortion(distort_limit=0.2, p=1.0),
        # Distort Image Elastically
        A.ElasticTransform(alpha_affine=0.2, p=1.0),
        A.OneOf([
            # Add a yellow sun flare
            A.RandomSunFlare(flare_roi=(0.2, 0.2, 1, 0.5), angle_lower=0.5, num_flare_circles_lower=4, src_radius=100,
                             src_color=(204, 255, 255), p=0.15),
            # Add a red sun flare
            A.RandomSunFlare(flare_roi=(0.2, 0.2, 1, 0.5), angle_lower=0.5, num_flare_circles_lower=4, src_radius=100,
                             src_color=(204, 204, 255), p=0.15),
        ]),
    ]

    def __init__(self, resize_to):
        self.transforms = A.Compose([
            A.Resize(resize_to, resize_to),
            *TrainTransforms.augments,
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
                ),
            ToTensorV2()
        ])
    
    def __call__(self, img):
        bla = self.transforms(image=np.array(img))['image']
        return bla


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
    all_images = glob.glob(f'{ROOT_DIR}/00005/*.ppm')

    transform = A.Compose([
        A.Resize(RESIZE_TO, RESIZE_TO),
        *TrainTransforms.augments
    ])

    random.seed(42)

    for i, image_path in enumerate(all_images):
        # Read the image.
        image = cv2.imread(image_path)
        orig_image = image.copy()
        # Apply the image transforms.
        image_tensor = transform(image=image)['image']

        orig_image = cv2.resize(orig_image, (RESIZE_TO, RESIZE_TO))
        img_concat = cv2.hconcat([
            np.array(orig_image, dtype=np.uint8),
            np.array(image_tensor, dtype=np.uint8)
        ])
        cv2.imshow('Result', img_concat)
        cv2.waitKey(0)

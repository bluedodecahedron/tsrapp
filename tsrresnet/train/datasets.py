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


def random_lines(img, **kwargs):
    min_col_shift = [-30, -10, -30]
    max_col_shift = [10, 0, 10]
    width = img.shape[1]
    height = img.shape[0]
    num_lines = 1+int(10*random.random())
    new_img = img
    avg_color_per_row = np.average(new_img, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    for i in range(num_lines):
        r = []
        for j in range(8):
            r.append(random.random())
        R = int(avg_color[0]+min_col_shift[0]+r[4]*(max_col_shift[0]-min_col_shift[0])*2)
        G = int(avg_color[1]+min_col_shift[1]+r[5]*(max_col_shift[1]-min_col_shift[1])*2)
        B = int(avg_color[2]+min_col_shift[2]+r[6]*(max_col_shift[2]-min_col_shift[2])*2)
        if R < 0:
            R = 0
        if G < 0:
            G = 0
        if B < 0:
            B = 0
        new_img = cv2.line(
            img=new_img,
            pt1=(int(r[0]*width), int(r[1]*height)),
            pt2=(int(r[2]*width), int(r[3]*height)),
            color=(R, G, B),
            thickness=1+int(r[7]*3)
        )
    return new_img


# Training transforms.
class TrainTransforms:
    augments = [
        # Random elastic transform
        A.ElasticTransform(alpha=200, alpha_affine=0, sigma=10, p=0.5),
        # Random Shift, Scale, Perspective
        A.OneOf([
            # Random Shift, Scale
            A.ShiftScaleRotate(shift_limit=0.1, scale_limit=(0.3, 0.5), rotate_limit=0, p=0.4),
            # Perspective
            A.Perspective(scale=(0.05, 0.15), p=0.6),
        ], p=1.0),
        # Random color changes
        A.ColorJitter(brightness=(0.8, 1.2), contrast=(0.8, 1.2), saturation=(0.8, 1.2), hue=(-0.1, 0.1), p=0.8),
        # Random Sharpen
        A.Sharpen(alpha=(0.3, 0.4), lightness=(1.0, 1.0), p=0.6),
        # Random shadow
        A.RandomShadow(shadow_roi=(0, 0, 1, 0.75), num_shadows_lower=1, num_shadows_upper=1, shadow_dimension=3, p=0.4),
        # Add random lines
        A.Lambda(image=random_lines, p=1.0),
        # Reduce image quality
        A.OneOf([
            # Random motion blur
            A.MotionBlur(blur_limit=(7, 21), p=0.2),
            # Random defocus blur
            A.Defocus(alias_blur=(0.5, 0.7), p=0.1),
            # Use downsampling, simulating far away traffic signs
            A.Sequential([
                A.RandomScale(scale_limit=(-0.90, -0.80), p=1.0),
                A.ImageCompression(quality_lower=80, quality_upper=90, p=0.5),
                A.Resize(RESIZE_TO, RESIZE_TO),
            ], p=0.7),
        ], p=0.7),
        # Random Noise
        A.GaussNoise(var_limit=(50.0, 100.0), p=0.33),
        # Simulates weather
        A.OneOf([
            # Simulates mud
            A.Spatter(mode="mud", p=0.3),
            # Simulates fog
            A.RandomFog(p=0.3),
            # Simulates rain
            A.RandomRain(p=0.3),
            # Add a yellow sun flare
            A.RandomSunFlare(flare_roi=(0.0, 0.0, 1, 1), angle_lower=0.5,
                             num_flare_circles_lower=3, num_flare_circles_upper=6, src_radius=70,
                             src_color=(204, 255, 255), p=0.05),
            # Add a red sun flare
            A.RandomSunFlare(flare_roi=(0.0, 0.0, 1, 1), angle_lower=0.5,
                             num_flare_circles_lower=3, num_flare_circles_upper=6, src_radius=70,
                             src_color=(204, 204, 255), p=0.05),
        ], p=0.25),
    ]

    def __init__(self):
        self.transforms = A.Compose([
            A.Resize(RESIZE_TO, RESIZE_TO),
            *TrainTransforms.augments,
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
    def __init__(self):
        self.transforms = A.Compose([
            A.Resize(RESIZE_TO, RESIZE_TO),
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
        transform=(TrainTransforms())
    )
    dataset_test = datasets.ImageFolder(
        ROOT_DIR, 
        transform=(ValidTransforms())
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
    all_images = glob.glob(f'{ROOT_DIR}/00003/*.ppm')

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

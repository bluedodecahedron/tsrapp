import os

import torch
import albumentations as A
import numpy as np
import cv2
import glob as glob
import random
import PIL
import math

from torchvision import datasets
from torch.utils.data import DataLoader, Subset, Dataset
from albumentations.pytorch import ToTensorV2

# Required constants.
ROOT_DIR = '../input/GTSRB_Final_Training_Images/GTSRB/Final_Training/Images'
VALID_SPLIT = 0.1
RESIZE_TO = 224 # Image size of resize when applying transforms.
BATCH_SIZE = 32
NUM_WORKERS = 4 # Number of parallel processes for data preparation.


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


def random_remove(img, **kwargs):
    width = img.shape[1]
    height = img.shape[0]
    min_aspect_ratio = 1
    max_aspect_ratio = 5
    min_area_ratio = 0.05
    max_area_ratio = 0.1
    min_rect_width = width/6
    min_rect_height = height/6
    max_rect_width = width/3
    max_rect_height = height/3
    max_dist_width = width/5
    max_dist_height = height/5
    area = width * height

    for attempt in range(5):
        # define random variables
        r = []
        for j in range(6):
            r.append(random.random())

        rectangle_area = random.uniform(min_area_ratio, max_area_ratio) * area
        aspect_ratio = random.uniform(min_aspect_ratio, max_aspect_ratio)
        if r[0] > 0.5:
            aspect_ratio = 1/aspect_ratio

        h = int(math.sqrt(rectangle_area * aspect_ratio))
        w = int(math.sqrt(rectangle_area / aspect_ratio))

        if max_dist_width+w < width and max_dist_height+h < height:
            # Define points of the rectangle
            if r[1] < 0.5:
                x1 = int(max_dist_width*r[2])
                x2 = x1 + w
            else:
                x2 = int(width-max_dist_width*r[2])
                x1 = x2 - w
            if r[3] < 0.5:
                y1 = int(max_dist_height*r[4])
                y2 = y1 + h
            else:
                y2 = int(height-max_dist_height*r[4])
                y1 = y2 - h

            # Generate Gaussian noise
            noise = np.random.randn(*img[y1:y2, x1:x2].shape) * 50

            # Add the noise to the image
            img[y1:y2, x1:x2] = noise

            return img

    return img


def erode(img, **kwargs):
    size = 4 + int(5*random.random())
    kernel = np.ones((size, size), np.uint8)
    img_erode = cv2.erode(img, kernel, iterations=1)
    return img_erode


def dilate(img, **kwargs):
    size = 4 + int(5*random.random())
    kernel = np.ones((size, size), np.uint8)
    img_dilate = cv2.dilate(img, kernel, iterations=1)
    return img_dilate


# Training transforms.
class TrainTransforms:
    augments = A.Compose([
        A.Sharpen(lightness=(1.0, 1.0), p=0.3),
        # Random color changes
        A.ColorJitter(brightness=(0.8, 1.2), contrast=(0.8, 1.2), saturation=(0.8, 1.2), hue=(-0.05, 0.05), p=0.8),
        # Randomly thicken or thin shapes
        A.OneOf([
            A.Lambda(name='Dilate', image=dilate, p=0.5),
            A.Lambda(name='Erode', image=erode, p=0.5),
        ], p=0.2),
        A.OneOf([
            A.Sequential([
                A.ShiftScaleRotate(shift_limit=0.05, scale_limit=(0.2, 0.4), rotate_limit=10, p=0.9),
                # Randomly distort image
                A.GridDistortion(distort_limit=0.2, p=0.2),
            ], p=0.7),
            # Perspective
            A.Perspective(scale=(0.05, 0.10), p=0.3),
        ], p=0.9),
        A.OneOf([
            A.GaussNoise(var_limit=(10, 40), p=0.2),
            A.ImageCompression(quality_lower=20, quality_upper=50, p=0.2),
        ], p=0.4),
        # Random shadow
        A.RandomShadow(shadow_roi=(0, 0, 1, 0.75), num_shadows_lower=1, num_shadows_upper=1, shadow_dimension=3, p=0.2),
        # Operations that can reduce image quality
        A.OneOf([
            # Randomly replace rectangular image parts with noise
            A.Lambda(name='RandomRemove', image=random_remove, p=0.2),
            # Use downsampling, simulating far away traffic signs
            A.Sequential([
                A.RandomScale(scale_limit=(-0.90, -0.80), p=1.0),
                A.ImageCompression(quality_lower=80, quality_upper=90, p=0.5),
                A.Resize(RESIZE_TO, RESIZE_TO),
            ], p=0.3),
            # Simulate fog
            A.RandomFog(p=0.1),
            # Simulate rain
            A.RandomRain(brightness_coefficient=1.0, p=0.1),
            # Add a yellow sun flare
            A.RandomSunFlare(flare_roi=(0.0, 0.0, 1, 1), angle_lower=0.5,
                             num_flare_circles_lower=3, num_flare_circles_upper=6, src_radius=100,
                             src_color=(204, 255, 255), p=0.1),
            # Add a red sun flare
            A.RandomSunFlare(flare_roi=(0.0, 0.0, 1, 1), angle_lower=0.5,
                             num_flare_circles_lower=3, num_flare_circles_upper=6, src_radius=100,
                             src_color=(204, 204, 255), p=0.1),
        ], p=0.7),
    ], p=0.90)

    def __init__(self):
        self.transforms = A.Compose([
            A.Resize(100, 100),
            A.Resize(int(RESIZE_TO*1.1), int(RESIZE_TO*1.1)),
            A.CenterCrop(RESIZE_TO, RESIZE_TO),
            TrainTransforms.augments,
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
                ),
            ToTensorV2()
        ])
    
    def __call__(self, img):
        return self.transforms(image=np.array(img))['image']

    def __str__(self):
        return self.transforms.__str__()


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


class CustomImageFolderDataset(datasets.ImageFolder):
    """
    Infer from standard PyTorch Dataset class
    Such datasets are often very useful
    """

    def __init__(self, root, transform, mix_up_p=0.0, mix_up_alpha=0.0, horizontal_flip_p=0.0):
        super().__init__(root, transform)
        self.mix_up_p = mix_up_p
        self.mix_up_alpha = mix_up_alpha
        self.horizontal_flip_p = horizontal_flip_p

    def __getitem__(self, idx):
        image, label = super().__getitem__(idx)
        num_classes = len(self.classes)

        # Flip Image horizontal for images where it's possible
        if label not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 14, 19, 20, 33, 34, 36, 37, 38, 39, 43, 44, 46, 47]:
            flip = A.Compose([
                A.HorizontalFlip(p=self.horizontal_flip_p),
                ToTensorV2(),
            ])
            # Permute image dimensions because when converting to numpy, the image gets transposed (not what we want)
            image = flip(image=image.permute(1, 2, 0).numpy())['image']

        if label == 57:
            downscale = A.Compose([
                    A.OneOf([
                        A.Resize(5, 5),
                        A.Resize(10, 10),
                        A.Resize(20, 20),
                        A.Resize(30, 30),
                        A.Resize(50, 50),
                        A.Resize(70, 70),
                    ], p=1.0),
                    A.Resize(RESIZE_TO, RESIZE_TO),
                    ToTensorV2(),
                ])
            image = downscale(image=image.permute(1, 2, 0).numpy())['image']

        # Change label to one-hot vector
        label = torch.zeros(num_classes)
        label[self.targets[idx]] = 1

        # Apply mixup
        p = random.random()
        if p < self.mix_up_p:
            mixup_idx = random.randint(0, self.__len__() - 1)
            mixup_image, mixup_label = super().__getitem__(mixup_idx)

            mixup_label = torch.zeros(num_classes)
            mixup_label[self.targets[mixup_idx]] = 1

            # Select a random number from the given beta distribution
            # Mixup the images accordingly
            lam = np.random.beta(self.mix_up_alpha, self.mix_up_alpha)
            image = lam * image + (1 - lam) * mixup_image
            label = lam * label + (1 - lam) * mixup_label

        return image, label


def get_datasets(root=ROOT_DIR):
    """
    Function to prepare the Datasets.

    Returns the training and validation datasets along 
    with the class names.
    """
    aug_config = {
        'transform': (TrainTransforms()),
        'mix_up_p': 0.0,
        'mix_up_alpha': 0.1,
        'horizontal_flip_p': 0.4,
    }

    dataset = CustomImageFolderDataset(
        root=root,
        transform=aug_config['transform'],
        mix_up_p=aug_config['mix_up_p'],
        mix_up_alpha=aug_config['mix_up_alpha'],
        horizontal_flip_p=aug_config['horizontal_flip_p']

    )
    dataset_test = CustomImageFolderDataset(
        root=root,
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

    return dataset_train, dataset_valid, dataset.classes, aug_config


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
    all_images += glob.glob(f'{ROOT_DIR}/*/*.jpg')
    all_images += glob.glob(f'{ROOT_DIR}/*/*.png')
    random.shuffle(all_images)

    transform = A.Compose([
        A.Resize(224, 224),
        TrainTransforms.augments,
        A.Resize(RESIZE_TO, RESIZE_TO),
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

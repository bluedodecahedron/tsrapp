# TSDRapp

Android App for detecting and classifying traffic signs as part of my Bachelor's thesis in Software and Information Engineering at TU Wien.

![](activetrafficsigns.jpg)

Some key information about the project:

* TSDRapp can detect and recognize the 48 most common signs in the Vienna convention of road signs and signals. 
* The backend is given as a django project. It receives a video stream from the frontend in real time to recognize traffic signs.
* The frontend is given as an android app. It receives a video stream from the backend containing recognized traffic signs in real time.
* The object detection model used in this project is the pytorch implementation of yoloX. 
* The object recognition model used in this project is EfficientNet, also implemented with pytorch. 
* The video streaming technology used in this project is WebRTC.

# Installation

## 1. Clone repository

Clone this project to your local machine (Windows or Linux). 

On Windows, keep the following in mind:
* CMake and Visual Studio Build Tools (2022) need to be installed.
* Installation commands below need to be run from within the Visual Studio developer console. 

## 2. Create new python environment and install dependencies

All python dependencies for this project are given in the file "conda_env.yml". It is highly recommended to use an
anaconda environment and install all dependencies like so:

```conda env create -f conda_env.yml -n tsdr```

On Linux, some python dependencies may need to be changed. `pycocotools` is one of them.
Installation can take a considerable amount of time. When it's done, activate the environment with

```conda activate tsdr```

It is discouraged from using pip alone since the conflict resolution is not as good as the one from conda, so it may not work.
This is because multiple included python libraries require the same dependencies, but with different versions.

## 3. Install tsdyolox

Navigate into the tsdyolox folder and run the following command. Make sure you have activated the conda environment from step 2.

```shell
pip3 install -v -e .  # or  python3 setup.py develop
```

A customized fork of the original yoloX github project is included in this project as a submodule.

## 4. Install tsrmodel

Navigate into the tsrmodel folder and run the following command. Make sure you have activated the conda environment from step 2.

```shell
pip3 install -v -e .  # or  python3 setup.py develop
```

The basic architecture of the traffic sign recognition implementation is taken from 
[here](https://debuggercafe.com/traffic-sign-recognition-using-pytorch-and-deep-learning/).

However, the implementation in the above link uses Mobilenet, while this project uses EfficientNet since it is better optimized for real time classification.
The traffic sign images also needed additional augmentations since real world performance was not good enough without them.
Model inference also needed to be changed in order for it to work with this project.

## 6. Run backend on local computer

Navigate into the backend folder and follow the instructions given there.

## 5. Run frontend on android device

The frontend is given as an Android app. 

Navigate into the frontend folder and follow the instructions given there.

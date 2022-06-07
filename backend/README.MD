# Backend API service with django

This project represents the backend server for the TSDR App. It provides an API that allows traffic sign detection in images.

## Installation

### 1. Install package dependencies

This project uses the following python packages:
* django: Django provides the backend architecture for the project
* django-ninja: Django ninja provides REST API support for django
* mod-wsgi: For future apache server support

Install them using the command

`pip install -r requirements.txt`

### 2. Install yoloX

The object detection algorithm used in this project is yoloX. A customized fork of the original yoloX github project is included in this project as a submodule.

YoloX needs to be installed in the active python environment in order for the detection to work. Navigate to the submodule folder and follow the installation instructions given there in the README.

### 3. Build database

This command adds all django models to the database that are necessary to use the backend

`python manage.py migrate`

### 4. Start the backend server

This command will start the backend server

`python manage.py runserver [port]`

## API Doc

Documentation for all API Endpoints is available at

`localhost:[port]/api/docs`

## Quickstart

### 1. Create admin user

In order to access the admin interface, an admin user needs to be created first.

`python manage.py createsuperuser --username=[username] --email=[email]`

### 2. Create new user

To create a new user, log into the admin interface with the newly created admin at

`localhost:[port]/admin`

### 3. User login

To execute a login request, open the API docs at /api/docs. Then execute the login endpoint below.

`POST /api/authentication/login`

Checking the logging status can be done with

`GET /api/authentication/status`

### 4. Traffic sign detection

When logged in as an existing user, traffic sign detection can also be done within the API docs. Use the endpoint below to upload an image for traffic sign detection.

`POST api/tsdr/trafficimg`

When successful, the request returns box coordinates of the detected traffic signs within the image. It also creates an image visualizing the result in the folder storage/tsd
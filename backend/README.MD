# TSR Backend API Service with Django

## Installation

### 1. Install Dependencies

Django provides the backend architecture for the project

`pip install django`

Django ninja provides REST API support for django

`pip install django-ninja`

### 2. Build database

This adds all necessary models to the database

`python manage.py migrate`

### 3. Start the backend server

`python manage.py runserver [port]`

## API Doc

Documentation for all available Ninja API Endpoints can be accessed with

    Method: GET
    URL: /api/docs

## Quickstart

### 1. Create admin user

Necessary to access admin interface

`python manage.py createsuperuser --username=[username] --email=[email]`

### 2. Create new user

At the endpoint below you can access the admin interface and create new users. 

    Method: GET
    URL: /admin

A user can be used to authenticate in the API.

### 3. Login user

At the endpoint below you can login as any created user

    Method: POST
    URL: /api/authentication/login
    Body: { 
        "username": [username], 
        "password": [password] 
    }

And check the login status at

    Method: GET
    URL: /api/authentication/status
# Backend API service with django

This project represents the backend server for the TSDR App. It provides an API that allows traffic sign detection in video streams.

## Installation

### 1. Backend dependencies

The backend dependencies should already be installed by the instructions given in the README of the parent folder.
Make sure that the right conda environment is activated.

The following major technologies are used:
* django: Provides the framework for the backend server
* django-ninja: Provides a REST interface for django
* uvicorn: Provides asynchronous event and request handling. This is needed for WebRTC to work.
* aiortc: Provides a WebRTC implementation for python. This is needed for video streaming to work between backend and frontend.
* yolox: Provides a model and algorithm for traffic sign detection.
* resnet: Provides a model for traffic sign recognition.
* pytorch: Provides a machine learning framework for yolox and resnet.

### 3. Build database

This command adds all django models to the database that are necessary to use the backend. 
Make sure you are in the base folder of the project.

`python manage.py migrate`

### 4. Add public host file

If the server should be accessible from an address other than "localhost", a text file "public_hosts.txt" needs to be added
into the folder backend/backend containing that address. More than one can be added, seperated by lines.


### 5. Open network ports

In WebRTC, public TURN servers are used to exchange ice candidates between peers. The TURN protocol uses certain network ports to do this.
Depending on the type of connection, these ports may need to be opened for it to work. 
In most cases, this should not be necessary. If exchanging ice candidates fails however, opening these ports may help.

```UDP ports 49152-65535```

### 5. Start the backend server

This command will start the backend server. Make sure you are in the base folder of the project.

`python -m uvicorn backend.asgi:application --host 0.0.0.0 --port [port] --reload`

## API Doc

Documentation for all API Endpoints is available at

`localhost:[port]/api/docs`

## Other Interaction with the backend

### 1. Create admin user

In order to access the admin interface, an admin user needs to be created first.

`python manage.py createsuperuser --username=[username] --email=[email]`

### 2. Create new user

To create a new user, log into the admin interface with the newly created admin at

`localhost:[port]/admin`

### 3. User login

To execute a login request, open the API docs at /api/docs. Then execute the login endpoint below.

`POST /api/authentication/login`

The login status can be seen at

`GET /api/authentication/status`

### 4. Single Image Traffic sign Detection

When logged in as an existing user, traffic sign detection can also be done within the API docs. Use the endpoint below to upload an image for traffic sign detection.

`POST api/tsdr/trafficimg`

When successful, the request creates an image visualizing the result in the folder storage/tsd

### 5. Video Streaming Traffic Sign Detection

To send a video stream for detection to the backend from the local computer, open the following in a browser

`localhost:[port]/api/webrtc/client/client.html`

This should open an html page containing a javascript implementation of webrtc ([source](https://github.com/aiortc/aiortc/blob/main/examples/server/client.js)). A stream can be sent to the backend
through choosing either a real or a virtual camera (such as the one from OBS). Keep in mind that media permissions
need to be enabled in the browser settings for this to work since most browsers nowadays 
don't allow http websites to use usermedia.
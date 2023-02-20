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
* efficientnet: Provides a model for traffic sign recognition.
* pytorch: Provides a machine learning framework for yolox and efficientnet.

### 2. Download server resources

The backend server uses pytorch models for its TSDR purposes. Some automated tests in the backend project also require additional images that are too large for a git repository. Download the needed resources from the following Google Drive:

https://drive.google.com/file/d/1WNN6ZGW7hNsqLFhdUfXgoK0WARX4uxIY/view?usp=sharing

Add the files into the folder backend/resources.

### 3. Execute tests

Make sure that TSDR inference works by executing all tests in the file `backend/app/apps/tsdr/tests.py`.
Some cv2 figures might pop up, which can be closed by pressing any key.

### 4. Build database

This command adds all django models to the database that are necessary to use the backend. 
Make sure you are in the base folder of the project.

`python manage.py migrate`

### 5. Create user

Since the backend is publicly hosted and exposes endpoints that create server-resources, a login is required to use it.
First, a user needs to be created in the django database.

An admin user can be created with the following command.

`python manage.py createsuperuser --username=[username] --email=[email]`

To create additional users, log into the admin interface with the newly created admin at

`localhost:[port]/admin`

### 6. Add public host file

If the server should be accessible from an address other than "localhost", a text file "public_hosts.txt" needs to be added
into the folder backend/backend containing that address. More than one can be added, seperated by lines.

### 7. Open network ports

In WebRTC, public TURN servers are used to exchange ice candidates between peers. The TURN protocol uses certain network ports to do this.
Depending on the type of connection, these ports may need to be opened for it to work. 
In most cases, this should not be necessary. If exchanging ice candidates fails however, opening these ports may help.

```UDP ports 49152-65535```

### 8. Start the backend server

This command will start the backend server. Make sure you are in the base folder of the project.

`python -m uvicorn backend.asgi:application --host 0.0.0.0 --port [port] --reload`

## Optional

The following is NOT needed if the backend only needs to be accessed from an Android device (see frontend project).

### 1. User login

To execute a login request, open the API docs at /api/docs. Then execute the login endpoint below.

`POST /api/authentication/login`

The login status can be seen at

`GET /api/authentication/status`

### 2. Video Streaming Traffic Sign Detection

To send a video stream for detection to the backend from the local computer, open the following in a browser

`localhost:[port]/api/webrtc/client/client.html`

This should open an html page containing a javascript implementation of webrtc ([source](https://github.com/aiortc/aiortc/blob/main/examples/server/client.js)). 
A stream can be sent to the backend through choosing either a real or a virtual camera (such as the one from OBS). 
Keep in mind that media permissions need to be enabled in the browser settings for this to work since most browsers nowadays don't allow http websites to use usermedia.

### API Doc

Documentation for all API Endpoints is available at

`localhost:[port]/api/docs`

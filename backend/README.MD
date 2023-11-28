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

The backend uses PyTorch models to do TSDR. They are too large for the git repository, but are available at:
https://drive.google.com/file/d/18sMf4xfe4xuGgkK416ua1UyS2bdPjP76/view?usp=sharing

The files need to be added to the folder `backend/resources`. The application will not work without them.

### 3. Execute tests

Make sure that TSDR inference works by executing all tests in the file `backend/app/apps/tsdr/tests.py`.
Some cv2 figures might pop up, which can be closed by pressing any key.

The file `backend/app/apps/tsdr/validation.py` can be used to perform TSDR validation on a test set and multiple videos. Keep in mind that processing the videos takes quite long (2 or 3 hours).

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

The port on which the application runs needs to be opened if the application is used outside the local network.

In WebRTC, public TURN servers are used to exchange ice candidates between peers. The TURN protocol uses certain network ports to do this.
Depending on the type of connection, these ports may need to be opened as well for it to work. 
In most cases, this should NOT be necessary. If exchanging ice candidates fails however, opening these ports may help.

```UDP ports 49152-65535```

### 8. Set Nvidia Clocks

For some Nivida GPUs, the (memory) clocks are not stable during model inference and will change if the GPU is not fully used. This can lead to varying inference speed, which is bad for performance of the server. To avoid this behavior, set the clocks manually with the following commands

`nvidia-smi -lgc 1770,1770` (GPU clocks)

`nvidia-smi -lmc 5001,5001` (memory clocks)

The needed (and available) clock values may vary depending on the GPU in use. 
For reference, on a RTX 3070, frame processing took 0.02 to 0.05 seconds.
If it takes any longer than 0.06 seconds, the application will not work correctly since this increases latency for each processed frame.

### 8. Start the backend server

This command will start the backend server. Make sure you are in the base folder of the project.

`python -m uvicorn backend.asgi:application --host 0.0.0.0 --port [port] --reload`

### 9. Connect with android device

Check frontend project for instructions on how to connect to the backend server. For each ended connection, a video is saved in the folder `backend/storage/videos`.

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

### 3. Validation

If you want to run the validation tests in the backend, you will need additional images and videos (7GB):
[missing]

Add them to `backend/resources`. The validation files are NOT necessary for the application to work.

### API Doc

Documentation for all API Endpoints is available at

`localhost:[port]/api/docs`

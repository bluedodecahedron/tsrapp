# Frontend app for android

This project represents the frontend for the TSDR app. It allows using a camera of an android device to detect traffic signs.

All devices running android version 5.0 (API level 21) to version 12.0 (API level 31) are supported. 

![](loginscreen.jpg)
![](startscreen.jpg)
![](tsdrscreen.jpg)

## Installation

There are two ways: 

Download the .apk file included in the latest release onto your android device and install it.

Or compile it yourself: Open the project in android studio and use the SDK manager to download android SDK 12.0 (API Level 31).

Create the file `app/src/main/res/raw/backend_host.txt`. In its first line, provide the host name and port number of the backend server. I.e. `localhost:8080` (this is also the default host assumed when no host is given within the file).

Run or build the project on an android device that has a camera installed (it will not work on devices that have no camera). Keep in mind that android emulators will not work with this app since they can't simulate cameras.

## Quickstart

When starting the app, a login screen appears. Supply credentials of users that were manually added to the backend database (see backend documentation for more information on this).

After logging in, the app shows a start button. After pressing it, a video stream should show up highlighting recognized traffic signs. Keep in mind that the backend needs to run for this to work. 

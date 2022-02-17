Project:
Shared Photo Library Organizer

Project Members:
Berk Güler 2310092
Onur Demir 2309870

This project includes server.py, client.py, user.py, photo.py, collection.py, view.py, *.txt(test and requirements.txt

phase1.py includes all the classes namely, Photo, Collection, View and User, and their module implementations.

requirements.txt includes all the necessary libraries in order to reproduce the environment.

Extra modules that are used:
from PIL import Image as PILIMAGE  # in order to open the image from given path
from exif import Image as EXIFIMAGE  # in order to get datetime value of image
from GPSPhoto import gpsphoto  # in order to get latitude and longitude values
import pymongo
from pymongo import MongoClient


Installation/Run Process:

1) Install virtualenv
$ pip3 install virtualenv 

2) Check installation
$ virtualenv --version

3) Python version should be greater than 3.0.0
$ python --version

4) Creating and preparing virtual environment
$ virtualenv my_name
$ virtualenv -p /usr/bin/python3 virtualenv_name
$ source virtualenv_name/bin/activate

5) Install pip3
$ sudo apt-get -y install python3-pip
$ sudo apt install mongodb-compass

6) Install necessary libraries

$ pip3 install Pillow
$ pip3 install exif
$ pip3 install gpsphoto
$ pip3 install piexif  //Required for gpsphoto
$ pip3 install exifread //Required for gpsphoto
$ pip3 install pymongo


7) Run server.py and client.py

$ python3 demo.py

8) Deactivate virtual environment after you finished

(virtualenv_name)$ deactivate



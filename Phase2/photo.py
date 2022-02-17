from PIL import Image as PILIMAGE  # in order to open the image from given path
from exif import Image as EXIFIMAGE  # in order to get datetime value of image
from GPSPhoto import gpsphoto  # in order to get latitude and longitude values
import pymongo
import base64
from helpers import *
class Photo:
    class_counter = 0
    def __init__(self,path,id, img=None, location=None, date_time=None, tags=None, collection_ids=None, view_ids=None):


        # initialize the values to created photo object
        if id == None:
            with open(path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read())
                
            # open the image with PIL and save it to self.img
            # open the image and get the datetime info
            with open(path, 'rb') as image_file:
                my_image = EXIFIMAGE(image_file)

            if 'datetime_original' in my_image.list_all(): datetime = my_image.datetime_original
            else: datetime = None
            # get the GPS info of the photo
            data = gpsphoto.getGPSData(path)
            if 'Latitude' in data and 'Longitude' in data:
                latitude = data['Latitude']
                longitude = data['Longitude']
            else:
                latitude = None
                longitude = None
            self.id = Photo.class_counter
            self.img = PILIMAGE.open(path)
            self.location = [longitude, latitude]
            self.date_time = datetime
            self.tags = []
            self.collection_ids = []
            self.view_ids = []
            Photo.class_counter += 1
            photos = photos_table()
            photo = {
                "_id" : self.id,
                "img" : encoded_image,
                "location" : self.location,
                "date_time" : self.date_time,
                "tags" : self.tags,
                "collection_ids" : self.collection_ids,
                "view_ids" : self.view_ids
            }
            photos.insert_one(photo)
            close_connection_to_db()
        else:
            self.id = id
            self.img = img
            self.location = location
            self.date_time = date_time
            self.tags = tags
            self.collection_ids = collection_ids
            self.view_ids = view_ids

    # add given tag to tag list of the photo object
    def addTag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
            photos = photos_table()
            photos.find_one_and_update({"_id" : self.id}, {"$set" : {"tags" : self.tags}})
            close_connection_to_db()
            message = str("Tag is added.")
        else:
            message = str("The photo already has this tag.")
            notify = None
        return message,notify

    # remove given tag from the tag list of the photo object
    def removeTag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            photos = photos_table()
            photos.find_one_and_update({"_id" : self.id}, {"$set" : {"tags" : self.tags}})
            close_connection_to_db()
            message = str("Tag is removed.")
        else:
            message = str("Tag is not in the tag list.")
        return message
    # set the location of the photo object to given longitude and latitude values
    def setLocation(self, long, latt):
        self.location = [long, latt]
        photos = photos_table()
        photos.find_one_and_update({"_id" : self.id}, {"$set" : {"location" : self.location}})
        close_connection_to_db()
        message = str("Location is added.")
        return message
        

    # remove the location information of photo object, assign it to None
    def removeLocation(self):
        self.location = [None, None]
        photos = photos_table()
        photos.find_one_and_update({"_id" : self.id}, {"$set" : {"location" : self.location}})
        close_connection_to_db()
        message = str("Location is removed.")
        return message

    # set the datetime of the photo object to given datetime value
    def setDateTime(self, date_time):
        self.date_time = date_time
        photos = photos_table()
        photos.find_one_and_update({"_id" : self.id}, {"$set" : {"date_time" : self.date_time}})
        close_connection_to_db()
        message = str("Date_time is added.")
        return message
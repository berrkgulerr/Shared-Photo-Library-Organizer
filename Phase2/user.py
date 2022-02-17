from sys import meta_path
import os
from photo import *
from collection import *
from view import *
from helpers import *
import json
import pymongo
import base64
from PIL import Image as PILIMAGE  # in order to open the image from given path
class User:
    class_counter = 0
    def __init__(self,id, username, password, photo_ids=None, collection_ids=None,view_ids=None):

        if id == None:
            self.id = User.class_counter
            self.username = username
            self.password = password
            self.photo_ids = []
            self.collection_ids = []
            self.view_ids = []
            User.class_counter += 1
            users = users_table()
            user = {
                "_id" : self.id,
                "username" : self.username,
                "password" : self.password,
                "photo_ids" : self.photo_ids,
                "collection_ids" : self.collection_ids,
                "view_ids" : self.view_ids
            }
            users.insert_one(user)
            close_connection_to_db()
        else:
            self.id = id
            self.username = username
            self.password = password
            self.photo_ids = photo_ids
            self.collection_ids = collection_ids
            self.view_ids = view_ids
    def create_photo(self, path):
        myphoto = Photo(id = None, path = path)
        users = users_table()
        users.find_one_and_update({"_id":self.id}, {"$push" : {"photo_ids" : myphoto.id}})
        close_connection_to_db()
        message = str("Photo successfully added to the user account.")
        return message

    def add_tag(self, photo_id, tag):
        if photo_id in self.photo_ids:
            photos = photos_table()
            curr_photo = photos.find_one({"_id" : photo_id})
            tofile = base64.b64decode(curr_photo['img'])
            fh = open("temp.jpg","wb")
            fh.write(tofile)
            fh.close()
            myimg = PILIMAGE.open("temp.jpg")
            os.remove("temp.jpg")
            photo = Photo(None,curr_photo['_id'], myimg, curr_photo['location'], curr_photo['date_time'], curr_photo['tags'], curr_photo['collection_ids'], curr_photo['view_ids'])
            close_connection_to_db()
            message = photo.addTag(tag)
        else:
            message = str("There is no photo with given id")
        return message

    def remove_tag(self, photo_id, tag):
        if photo_id in self.photo_ids:
            photos = photos_table()
            curr_photo = photos.find_one({"_id" : photo_id})
            tofile = base64.b64decode(curr_photo['img'])
            fh = open("temp.jpg","wb")
            fh.write(tofile)
            fh.close()
            myimg = PILIMAGE.open("temp.jpg")
            os.remove("temp.jpg")
            photo = Photo(None,curr_photo['_id'], myimg, curr_photo['location'], curr_photo['date_time'], curr_photo['tags'], curr_photo['collection_ids'], curr_photo['view_ids'])
            close_connection_to_db()
            message = photo.removeTag(tag)
        else:
            message = str("There is no photo with given id")
        return message

    def set_location(self, photo_id, long, latt):
        if photo_id in self.photo_ids:
            photos = photos_table()
            curr_photo = photos.find_one({"_id" : photo_id})
            tofile = base64.b64decode(curr_photo['img'])
            fh = open("temp.jpg","wb")
            fh.write(tofile)
            fh.close()
            myimg = PILIMAGE.open("temp.jpg")
            os.remove("temp.jpg")
            photo = Photo(None,curr_photo['_id'], myimg, curr_photo['location'], curr_photo['date_time'], curr_photo['tags'], curr_photo['collection_ids'], curr_photo['view_ids'])
            close_connection_to_db()
            message = photo.setLocation(long,latt)
        else:
            message = str("There is no photo with given id")
        return message

    def remove_location(self, photo_id):
        if photo_id in self.photo_ids:
            photos = photos_table()
            curr_photo = photos.find_one({"_id" : photo_id})
            tofile = base64.b64decode(curr_photo['img'])
            fh = open("temp.jpg","wb")
            fh.write(tofile)
            fh.close()
            myimg = PILIMAGE.open("temp.jpg")
            os.remove("temp.jpg")
            photo = Photo(None,curr_photo['_id'], myimg, curr_photo['location'], curr_photo['date_time'], curr_photo['tags'], curr_photo['collection_ids'], curr_photo['view_ids'])
            close_connection_to_db()
            message = photo.removeLocation()
        else:
            message = str("There is no photo with given id.")
        return message
        
    def set_date_time(self, photo_id, date_time):
        if photo_id in self.photo_ids:
            photos = photos_table()
            curr_photo = photos.find_one({"_id" : photo_id})
            tofile = base64.b64decode(curr_photo['img'])
            fh = open("temp.jpg","wb")
            fh.write(tofile)
            fh.close()
            myimg = PILIMAGE.open("temp.jpg")
            os.remove("temp.jpg")
            photo = Photo(None,curr_photo['_id'], myimg, curr_photo['location'], curr_photo['date_time'], curr_photo['tags'], curr_photo['collection_ids'], curr_photo['view_ids'])
            message = photo.setDateTime(date_time)
        else:
            message = str("There is no photo with given id.")
        return message

    def create_collection(self, name):
        mycol = Collection(id = None, owner_id=self.id, name = name)
        users = users_table()
        users.find_one_and_update({'_id':self.id}, {'$push': {'collection_ids': mycol.id}})
        close_connection_to_db()
        message = str("Collection is successfully created.")
        return message

    def add_photo(self, collection_id , photo_id):
        if collection_id in self.collection_ids:
            collections = collections_table()
            curr_col = collections.find_one({'_id': collection_id})
            collection = Collection(curr_col['_id'],curr_col['owner_id'],curr_col['name'],curr_col['photo_ids'],curr_col['view_ids'],curr_col['shared_user_ids'])
            close_connection_to_db()
            message = collection.addPhoto(photo_id)
        else:
            message = str("There is no collection with given id.")
        return message

    def remove_photo(self, collection_id, photo_id):
        if collection_id in self.collection_ids:
            collections = collections_table()
            curr_col = collections.find_one({'_id': collection_id})
            collection = Collection(curr_col['_id'],curr_col['owner_id'],curr_col['name'],curr_col['photo_ids'],curr_col['view_ids'],curr_col['shared_user_ids'])
            close_connection_to_db()
            message = collection.removePhoto(photo_id)
        else:
            message = str("There is no collection with given id.")
        return message

    def collection_fetch_photo(self, collection_id, photo_id):
        if collection_id in self.collection_ids:
            collections = collections_table()
            curr_col = collections.find_one({'_id': collection_id})
            collection = Collection(curr_col['_id'],curr_col['owner_id'],curr_col['name'],curr_col['photo_ids'],curr_col['view_ids'],curr_col['shared_user_ids'])
            close_connection_to_db()
            message = collection.fetchPhoto(photo_id)
        else:
            message = str("There is no collection with given id.")
        return message
        
    def add_view(self, collection_id, view_id):
        if collection_id in self.collection_ids:
            collections = collections_table()
            curr_col = collections.find_one({'_id': collection_id})
            collection = Collection(curr_col['_id'],curr_col['owner_id'],curr_col['name'],curr_col['photo_ids'],curr_col['view_ids'],curr_col['shared_user_ids'])
            close_connection_to_db()
            message = collection.addView(view_id)
        else:
            message = str("There is no collection with given id.")
        return message

    # clienttan istek user_id olarak verilecek server tarafında user listesinden bu idye sahip user bulunup fonksiyon çağırılacak
    def collection_share(self, collection_id, user_id):
        if collection_id in self.collection_ids:
            collections = collections_table()
            curr_col = collections.find_one({'_id': collection_id})
            collection = Collection(curr_col['_id'],curr_col['owner_id'],curr_col['name'],curr_col['photo_ids'],curr_col['view_ids'],curr_col['shared_user_ids'])
            close_connection_to_db()
            if self.id is collection.owner_id:
                message = collection.share(user_id)
            else:
                message = str("You are not the owner of this collection.")
        else:
            message = str("There is no collection with given id.")
        return message

    def collection_unshare(self, collection_id, user_id):
        if collection_id in self.collection_ids:
            collections = collections_table()
            curr_col = collections.find_one({'_id': collection_id})
            collection = Collection(curr_col['_id'],curr_col['owner_id'],curr_col['name'],curr_col['photo_ids'],curr_col['view_ids'],curr_col['shared_user_ids'])
            close_connection_to_db()
            if self.id is collection.owner_id:
                message = collection.unshare(user_id)
            else:
                message = str("You are not the owner of this collection.")
        else:
            message = str("There is no collection with given id.")
        return message

    def create_view(self, name):
        my_view = View(id = None, owner_id = self.id, name = name)
        users = users_table()
        users.find_one_and_update({'_id':self.id}, {'$push': {'view_ids': my_view.id}})
        close_connection_to_db()
        message = str("View is successfully created.")
        return message
    
    def set_tag_filter(self, view_id, taglist, conj):
        if view_id in self.view_ids:
            views = views_table()
            curr_view = views.find_one({'_id':view_id})
            view = View(curr_view['_id'],curr_view['owner_id'], curr_view['name'], curr_view['tags'],curr_view['conj'], curr_view['rectangle_location'],curr_view['time_interval'],curr_view['photo_ids'], curr_view['collection_ids'],curr_view['shared_user_ids'])
            close_connection_to_db()
            message = view.setTagFilter(taglist,conj)
        else:
            message = str("There is no view with given id.")
        return message

    def set_location_rect(self, view_id, rectangle):
        if view_id in self.view_ids:
            views = views_table()
            curr_view = views.find_one({'_id':view_id})
            view = View(curr_view['_id'],curr_view['owner_id'], curr_view['name'], curr_view['tags'],curr_view['conj'], curr_view['rectangle_location'],curr_view['time_interval'],curr_view['photo_ids'], curr_view['collection_ids'],curr_view['shared_user_ids'])
            close_connection_to_db()
            message = view.setLocationRect(rectangle)
        else:
            message = str("There is no view with given id.")
        return message

    def set_time_interval(self, view_id, start, end):
        if view_id in self.view_ids:
            views = views_table()
            curr_view = views.find_one({'_id':view_id})
            view = View(curr_view['_id'],curr_view['owner_id'], curr_view['name'], curr_view['tags'],curr_view['conj'], curr_view['rectangle_location'],curr_view['time_interval'],curr_view['photo_ids'], curr_view['collection_ids'],curr_view['shared_user_ids'])
            close_connection_to_db()
            message = view.setTimeInterval(start,end)
        else:
            message = str("There is no view with given id.")
        return message

    def get_tag_filter(self, view_id):
        if view_id in self.view_ids:
            views = views_table()
            curr_view = views.find_one({'_id':view_id})
            view = View(curr_view['_id'],curr_view['owner_id'], curr_view['name'], curr_view['tags'],curr_view['conj'], curr_view['rectangle_location'],curr_view['time_interval'],curr_view['photo_ids'], curr_view['collection_ids'],curr_view['shared_user_ids'])
            close_connection_to_db()
            message = view.getTagFilter()
        else:
            message = str("There is no view with given id.")
        return message

    def get_location_rect(self, view_id):
        if view_id in self.view_ids:
            views = views_table()
            curr_view = views.find_one({'_id':view_id})
            view = View(curr_view['_id'],curr_view['owner_id'], curr_view['name'], curr_view['tags'],curr_view['conj'], curr_view['rectangle_location'],curr_view['time_interval'],curr_view['photo_ids'], curr_view['collection_ids'],curr_view['shared_user_ids'])
            close_connection_to_db()
            message = view.getLocationRect()
        else:
            message = str("There is no view with given id.")
        return message

    def get_time_interval(self, view_id):
        if view_id in self.view_ids:
            views = views_table()
            curr_view = views.find_one({'_id':view_id})
            view = View(curr_view['_id'],curr_view['owner_id'], curr_view['name'], curr_view['tags'],curr_view['conj'], curr_view['rectangle_location'],curr_view['time_interval'],curr_view['photo_ids'], curr_view['collection_ids'],curr_view['shared_user_ids'])
            close_connection_to_db()
            message = view.getTimeInterval()
        else:
            message = str("There is no view with given id.")
        return message

    def view_share(self, view_id, user_id):
        if view_id in self.view_ids:
            views = views_table()
            curr_view = views.find_one({'_id':view_id})
            view = View(curr_view['_id'],curr_view['owner_id'], curr_view['name'], curr_view['tags'],curr_view['conj'], curr_view['rectangle_location'],curr_view['time_interval'],curr_view['photo_ids'], curr_view['collection_ids'],curr_view['shared_user_ids'])
            close_connection_to_db()
            if self.id is view.owner_id:
                message = view.share(user_id)
            else:
                message = str("You are not the owner of this view.")
        else:
            message = str("There is no view with given id.")
        return message

    def view_unshare(self, view_id, user_id):
        if view_id in self.view_ids:
            views = views_table()
            curr_view = views.find_one({'_id':view_id})
            view = View(curr_view['_id'],curr_view['owner_id'], curr_view['name'], curr_view['tags'],curr_view['conj'], curr_view['rectangle_location'],curr_view['time_interval'],curr_view['photo_ids'], curr_view['collection_ids'],curr_view['shared_user_ids'])
            close_connection_to_db()
            if self.id is view.owner_id:
                message = view.unshare(user_id)
            else:
                message = str("You are not the owner of this view.")
        else:
            message = str("There is no view with given id.")
        return message

    def view_update(self, view_id, flag, photo, info):
        view_flag = False
        for view in self.views:
            view.update(flag, photo, info)
            collection_flag = True
            break
        if (not collection_flag):
            raise Exception("There is no view with id: {}", view_id)
    
    def photo_list(self, view_id):
        if view_id in self.view_ids:
            views = views_table()
            curr_view = views.find_one({'_id':view_id})
            view = View(curr_view['_id'],curr_view['owner_id'], curr_view['name'], curr_view['tags'],curr_view['conj'], curr_view['rectangle_location'],curr_view['time_interval'],curr_view['photo_ids'], curr_view['collection_ids'],curr_view['shared_user_ids'])
            close_connection_to_db()
            message = view.photoList()
        else:
            message = str("There is no view with given id.")
        return message

    def view_fetch_photo(self, view_id, photo_id):
        if view_id in self.view_ids:
            views = views_table()
            curr_view = views.find_one({'_id':view_id})
            view = View(curr_view['_id'],curr_view['owner_id'], curr_view['name'], curr_view['tags'],curr_view['conj'], curr_view['rectangle_location'],curr_view['time_interval'],curr_view['photo_ids'], curr_view['collection_ids'],curr_view['shared_user_ids'])
            close_connection_to_db()
            message = view.fetchPhoto(photo_id)
        else:
            message = str("There is no view with given id.")
        return message

        

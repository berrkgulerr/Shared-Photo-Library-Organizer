import pymongo
from pymongo import MongoClient
con = pymongo.MongoClient("mongodb://localhost")
def users_table():
    con = pymongo.MongoClient("mongodb://localhost")
    db = con["shared_photo_library_organizer"]
    users = db["users"]
    return users
def photos_table():
    con = pymongo.MongoClient("mongodb://localhost")
    db = con["shared_photo_library_organizer"]
    photos = db["photos"]
    return photos
def collections_table():
    con = pymongo.MongoClient("mongodb://localhost")
    db = con["shared_photo_library_organizer"]
    collections = db["collections"]
    return collections
def views_table():
    con = pymongo.MongoClient("mongodb://localhost")
    db = con["shared_photo_library_organizer"]
    views = db["views"]
    return views
def close_connection_to_db():
    con.close()
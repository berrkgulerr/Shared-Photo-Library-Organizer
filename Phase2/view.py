from collection import *
from helpers import *
import base64
import pymongo

class View:
    class_counter = 0  # keeps the id value for View class objects
    # View class objects have a name, tags list which is initially empty, conjunctive boolean initially false,
    # locationRect and timeInterval filters which are initially empty lists, sharedUsers list which holds initially
    # owner of the object, photos list that are match with the filters of view object, owner, collectionID which is
    # -1 since it is not assigned to any collection yet, and id to identify.
    def __init__(self, id, owner_id, name, tags=None, conj=None, rectangle_location=None, time_interval=None, photo_ids=None, collection_ids=None, shared_user_ids=None):
        if id == None:
            self.id = View.class_counter
            self.owner_id = owner_id
            self.name = name
            self.tags = []
            self.conj = False
            self.rectangle_location = []
            self.time_interval = []
            self.photo_ids = []
            self.collection_ids = []
            self.shared_user_ids = []
            View.class_counter += 1
            views = views_table()
            view = {
                "_id" : self.id,
                "owner_id" : self.owner_id,
                "name" : self.name,
                "tags" : self.tags,
                "conj" : self.conj,
                "rectangle_location" : self.rectangle_location,
                "time_interval" : self.time_interval,
                "photo_ids" : self.photo_ids,
                "collection_ids" : self.collection_ids,
                "shared_user_ids" : self.shared_user_ids
            }
            views.insert_one(view)
            close_connection_to_db()
        else:
            self.id = id
            self.owner_id = owner_id
            self.name = name
            self.tags = tags
            self.conj = conj
            self.rectangle_location = rectangle_location
            self.time_interval = time_interval
            self.photo_ids = photo_ids
            self.collection_ids = collection_ids
            self.shared_user_ids = shared_user_ids

    # Set tags list to given taglist and conj to given conj input if not specified then it is false.
    def setTagFilter(self, taglist, conj=False):
        views = views_table()
        views.find_one_and_update({'_id': self.id}, {'$set': {'tags': taglist}})
        views.find_one_and_update({'_id': self.id}, {'$set': {'conj': conj}})
        close_connection_to_db()
        message = str("Tag filter is successfully set.")
        return message

    # Set locationRect list to given rectangle argument. Rectangle consists of list of 4 edge (long,latt) points,
    # starting from top left to bottom left in the clockwise direction.
    def setLocationRect(self, rectangle):
        views = views_table()
        views.find_one_and_update({'_id': self.id}, {'$set': {'rectangle_location': rectangle}})
        message = str("Rectangle location is successfully set.")
        return message

    # Set timeInterval list to given start end date_times.
    def setTimeInterval(self, start, end):
        self.time_interval = [start, end]
        views = views_table()
        views.find_one_and_update({'_id': self.id}, {'$set': {'time_interval': self.time_interval}})
        message = str("Time interval is successfully set.")
        return message
    # Get the tags from tags list and conj
    def getTagFilter(self):
        return self.tags, self.conj

    # Get locationRect
    def getLocationRect(self):
        return self.rectangle_location

    # Get timeInterval
    def getTimeInterval(self):
        return self.time_interval

    # Add given User to sharedUsers list of the view object and add view object to the views list of the given User.
    def share(self, user_id):
        if user_id not in self.shared_user_ids:
            views = views_table()
            users = users_table()
            views.find_one_and_update({'_id':self.id},{'$push':{'shared_user_ids':user_id}})
            users.find_one_and_update({'_id': user_id}, {'$push':{'view_ids': self.id}})
            message = str("The view is successfully shared with the user.")
            close_connection_to_db()
        else:
            message = str("The view is already shared with the user.")
        return message

    # Remove given User from sharedUsers list of the view object and remove view object from the views list of the given User.
    def unshare(self, user_id):
        if user_id in self.shared_user_ids:
            views = views_table()
            users = users_table()
            views.find_one_and_update({'_id':self.id},{'$pull':{'shared_user_ids':user_id}})
            users.find_one_and_update({'_id': user_id}, {'$pull':{'view_ids': self.id}})
            message = str("The view is successfully unshared with the user.")
            close_connection_to_db()
        else:
            message = str("The view is already not shared with the user.")
        return message

    # This function is called by collection when there is a modification in the collection object. If flag==1 it
    # means photo is added to collection else photo is removed from the collection If photo updated then,
    # it checks whether the added photo suits for the filters of the view object, if yes then photo is added to view
    # object's photo list. If photo removed then it removes the photo from the view object's photo list.
    def update(self, flag, photo, info):
        if (flag == 1):
            if self.conj:
                if set(self.tags).issubset(photo.tags):
                    if isinrect(photo.location, self.locationRect):
                        if self.timeInterval[0] <= photo.date_time <= self.timeInterval[1]:
                            self.photos.append(photo)
                            print("View with id",self.id  ,"is updated. Photo with id: ", photo.id, " is added to photo list of view")
            else:
                if any(x in self.tags for x in photo.tags):
                    if isinrect(photo.location, self.locationRect):
                        if self.timeInterval[0] <= photo.date_time <= self.timeInterval[1]:
                            self.photos.append(photo)
                            print("View with id",self.id ,"is updated. Photo with id: ", photo.id, " is added to photo list of view")
        elif(flag == 2):
            if photo in self.photos:
                self.photos.remove(photo)
                print("View with id",self.id , "is updated. Photo with id: ", photo.id, " is removed from the photo list of view")
        elif(flag == 3):
            if photo in self.photos:
                print("View with id",self.id , "is updated. Tag:", info, "is added the photo with id:", photo.id)
        elif(flag == 4):
            if photo in self.photos:
                print("View with id",self.id , "is updated. Tag:", info, "is removed from the photo with id:", photo.id)
        elif(flag == 5):
            if photo in self.photos:
                print("View with id",self.id , "is updated. Location:", info, "is added the photo with id:", photo.id)
        elif(flag == 6):
            if photo in self.photos:
                print("View with id",self.id , "is updated. Location is removed from the photo with id:", photo.id)
        elif(flag == 7):
            if photo in self.photos:
                print("View with id",self.id , "is updated. date_time:", info, "is added the photo with id:", photo.id)

    # This function creates an empty id_list array to hold id's. Then, it appends the id's of the photos that are in
    # the photo list of the view object. Finally, return the id_list list.
    def photoList(self):
        return self.photo_ids

    # Checks whether the photo with given photo id in view object's photo list.
    # If photo is found in list then show it by using PIL library, else print error.
    def fetchPhoto(self, photo_id):
        if photo_id in self.photo_ids:
            photos = photos_table()
            curr_photo = photos.find_one({"_id" : photo_id})
            tofile = base64.b64decode(curr_photo['img'])
            close_connection_to_db()
            fh = open("temp.jpg","wb")
            fh.write(tofile)
            fh.close()
            path = "temp.jpg"
            message = path
        else:
            message = str("Given photo is not in the view.")
        return message


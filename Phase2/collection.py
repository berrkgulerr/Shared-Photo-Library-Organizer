import pymongo
import os
from helpers import *
from view import *
from photo import *
import base64
from PIL import Image as PILIMAGE
def dot(A, B):
    return sum([A[i]*B[i] for i in range(len(B))])

# This function checks whether a point in a given rectangle area, by using dot products.
# Let's say P is the point and A-B-C-D are the edges of the rectangle from top left to bottom left(clokwise order).
# If (0 < AP.AB < AB.AB and 0 < AP.AD < AD.AD) then, we can say that point P is in the rectangle.
def isinrect(point, rectangle):
    if point[0] is not None and point[1] is not None:  # if point has latitude and longitude values
        AP = [point[0] - rectangle[0][0], point[1] - rectangle[0][1]]  # create a line from A to P
        AB = [rectangle[1][0] - rectangle[0][0], rectangle[1][1] - rectangle[0][1]]  # create a line from B to A
        AD = [rectangle[3][0] - rectangle[0][0], rectangle[3][1] - rectangle[0][1]]  # create a line from D to A
        if (0 < dot(AP,AB) < dot(AB, AB)) and (
                0 < dot(AP, AD) < dot(AD, AD)):  # check whether this point in the rectangle
            return True
        else:
            return False
    else:
        return False


class Collection:
    class_counter = 0  # keeps the id value for Collection class objects

    # Collection class objects have a name, photo list to hold photos that are in the collection object, sharedUsers to
    # hold Users who are shared with. views to hold added views, id to identify and owner for holding the owner who
    # is created the collection object.
    def __init__(self, id, owner_id, name, photo_ids=None, view_ids=None, shared_user_ids=None):
        if id == None:
            self.id = Collection.class_counter
            self.owner_id = owner_id
            self.name = name
            self.photo_ids = []
            self.view_ids = []
            self.shared_user_ids = []
            Collection.class_counter += 1
            collections = collections_table()
            collection = {
                "_id" : self.id,
                "owner_id" : self.owner_id,
                "name" : self.name,
                "photo_ids" : self.photo_ids,
                "view_ids" : self.view_ids,
                "shared_user_ids" : self.shared_user_ids
            }
            collections.insert_one(collection)
            close_connection_to_db()
        else:
            self.id = id
            self.owner_id = owner_id
            self.name = name
            self.photo_ids = photo_ids
            self.view_ids = view_ids
            self.shared_user_ids = shared_user_ids

    # If the given photo is not in the collection then add it to photos of the collection object. add collection id
    # to the added photo's collectionID list, in order to keep track of collections which includes the photo. call
    # update function of views in the collection with arguments 1 and photo. 1 stands for photo addition.
    def addPhoto(self, photo_id):
        if photo_id in self.photo_ids:
            message = str("Given photo is already in the collection.")
        else:
            collections = collections_table()
            photos = photos_table()
            collections.find_one_and_update({'_id': self.id}, {'$push': {'photo_ids': photo_id}})
            photos.find_one_and_update({'_id':photo_id}, {'$push':{'collection_ids':self.id}})
            close_connection_to_db()
            message = str("Given photo is added to the collection.")
        return message

            
    # if the given photo is in the collection then remove it from the photos of the collection object. remove
    # collection id from the removed photo's collectionID list, in order to keep track of collections which includes
    # the photo. call update function of views in the collection with arguments 2 and photo. 2 stands for photo removing.
    def removePhoto(self, photo_id):
        if photo_id not in self.photo_ids:
            message = str("Given photo is not in the collection.")
        else:
            collections = collections_table()
            photos = photos_table()
            collections.find_one_and_update({'_id': self.id}, {'$pull': {'photo_ids': photo_id}})
            photos.find_one_and_update({'_id':photo_id}, {'$pull':{'collection_ids':self.id}})
            close_connection_to_db()
            message = str("Given photo is removed from the collection.")
        return message

    # checks whether photo with id phid in photo list of the collection.
    # if exists show it nt using PIL library else print error.
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
            message = str("Given photo is not in the collection.")
        return message

    # This function creates photo list filtered with filters of the view. Adding photo list the view object.
    # Then, adding view object to the views list of the collection.
    def addView(self, view_id):
        if view_id not in self.view_ids:
            photos = photos_table()
            collections = collections_table()
            views = views_table()
            # get the filters from the view object
            curr_view = views.find_one({'_id': view_id})
            view = View(curr_view['_id'],curr_view['owner_id'],curr_view['name'],curr_view['tags'],curr_view['conj'],curr_view['rectangle_location'],curr_view['time_interval'],curr_view['photo_ids'],curr_view['collection_ids'],curr_view['shared_user_ids'])
            tagfilter, conj = view.getTagFilter()
            location = view.getLocationRect()
            time = view.getTimeInterval()
            print(time,location,tagfilter,conj)
            for photo_id in self.photo_ids:
                photos = photos_table()
                curr_photo = photos.find_one({"_id" : photo_id})
                tofile = base64.b64decode(curr_photo['img'])
                fh = open("temp.jpg","wb")
                fh.write(tofile)
                fh.close()
                myimg = PILIMAGE.open("temp.jpg")
                os.remove("temp.jpg")
                photo = Photo(None,curr_photo['_id'], myimg, curr_photo['location'], curr_photo['date_time'], curr_photo['tags'], curr_photo['collection_ids'], curr_photo['view_ids'])
                print(photo.tags,photo.location,photo.date_time)
                if conj:  # if conjunctive is true
                    result =  all(elem in photo.tags  for elem in tagfilter)
                    print(result)
                    if result:  # tag filters of the view must be subset of photo's tags.
                        if isinrect(photo.location, location):  # check whether photo in the view's rectangle area.
                            print(isinrect(photo.location, location))
                            if time[0] <= photo.date_time <= time[1]:  #check whether date_time of photo is in between of the view's time interval.
                                print("willupdate")
                                views.find_one_and_update({'_id':view_id}, {'$push' : {'photo_ids':photo_id}})  # if all conditions are true append photo the newphotos list.
                                photos.find_one_and_update({'_id':photo.id}, {'$push': {'view_ids':view_id}})
                else:
                    if any(x in tagfilter for x in photo.tags):  # checks if any of the tags are common.
                        if isinrect(photo.location, location):
                            if time[0] <= photo.date_time <= time[1]:
                                views.find_one_and_update({'_id':view_id}, {'$push' : {'photo_ids':photo_id}})  # if all conditions are true append photo the newphotos list.
                                photos.find_one_and_update({'_id':photo.id}, {'$push': {'view_ids':view_id}})# if all conditions are true append photo the newphotos list.
            collections.find_one_and_update({'_id':self.id}, {'$push':{'view_ids': view_id}})
            views.find_one_and_update({'_id':view_id}, {'$push' : {'collection_ids':self.id}})
            close_connection_to_db()
            message = str("View is successfully added to the collection.")
        else:
            message = str("View is already added to the collection.")
        return message
    # add user to the sharedUsers list of the collection, and add collection to the user's collection list
    # Since share function in the view says that, "otherwise only users having access to collection can access the view,
    # we call view.share() function for every view in views list of the collection"
    def share(self, user_id):
        if user_id not in self.shared_user_ids:
            collections = collections_table()
            users = users_table()
            collections.find_one_and_update({'_id':self.id},{'$push':{'shared_user_ids':user_id}})
            users.find_one_and_update({'_id': user_id}, {'$push':{'collection_ids': self.id}})
            message = str("The collection is successfully shared with the user.")
            close_connection_to_db()
        else:
            message = str("The collection is already shared with the user.")
        return message

    # Remove user from the sharedUsers list of the collection, and remove collection from the user's collection list
    def unshare(self, user_id):
        if user_id in self.shared_user_ids:
            collections = collections_table()
            users = users_table()
            collections.find_one_and_update({'_id':self.id},{'$pull':{'shared_user_ids':user_id}})
            users.find_one_and_update({'_id': user_id}, {'$pull':{'collection_ids': self.id}})
            message = str("The collection is successfully unshared with the user.")
            close_connection_to_db()
        else:
            message = str("The collection is already not shared with the user.")
        return message
from PIL import Image as PILIMAGE  # in order to open the image from given path
from exif import Image as EXIFIMAGE  # in order to get datetime value of image
from GPSPhoto import gpsphoto  # in order to get latitude and longitude values


class Photo:
    class_counter = 0  # keeps the id value for Photo class objects

    def __init__(self, path):
        self.img = PILIMAGE.open(path)  # open the image with PIL and save it to self.img

        # open the image and get the datetime info
        with open(path, 'rb') as image_file:
            my_image = EXIFIMAGE(image_file)
        if 'datetime_original' in my_image.list_all():
            datetime = my_image.datetime_original
        else:
            datetime = None

        # get the GPS info of the photo
        data = gpsphoto.getGPSData(path)
        if 'Latitude' in data and 'Longitude' in data:
            latitude = data['Latitude']
            longitude = data['Longitude']
        else:
            latitude = None
            longitude = None

        # initialize the values to created photo object
        self.location = [longitude, latitude]
        self.dateTime = datetime
        self.tags = []
        self.collectionID = []
        self.id = Photo.class_counter
        Photo.class_counter += 1

    # add given tag to tag list of the photo object
    def addTag(self, tag):
        self.tags.append(tag)

    # remove given tag from the tag list of the photo object
    def removeTag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
        else:
            print(tag, "is not in the tag list")
    # set the location of the photo object to given longitude and latitude values
    def setLocation(self, long, latt):
        self.location = [long, latt]

    # remove the location information of photo object, assign it to None
    def removeLocation(self):
        self.location = [None, None]

    # set the datetime of the photo object to given datetime value
    def setDateTime(self, datetime):
        self.dateTime = datetime

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
        print("No location information is found for the given image")
        return False

class Collection:
    class_counter = 0  # keeps the id value for Collection class objects

    # Collection class objects have a name, photo list to hold photos that are in the collection object, sharedUsers to
    # hold Users who are shared with. views to hold added views, id to identify and owner for holding the owner who
    # is created the collection object.
    def __init__(self, name, owner):
        self.name = name
        self.photos = []
        self.sharedUsers = [owner]
        self.views = []
        self.id = Collection.class_counter
        self.owner = owner
        owner.collections.append(self)
        Collection.class_counter += 1

    # if the given photo is not in the collection then add it to photos of the collection object. add collection id
    # to the added photo's collectionID list, in order to keep track of collections which includes the photo. call
    # update function of views in the collection with arguments 1 and photo. 1 stands for photo addition.
    def addPhoto(self, photo):
        if photo not in self.photos:
            self.photos.append(photo)
            photo.collectionID.append(self.id)
            for view in self.views:
                view.update(1, photo)

    # if the given photo is in the collection then remove it from the photos of the collection object. remove
    # collection id from the removed photo's collectionID list, in order to keep track of collections which includes
    # the photo. call update function of views in the collection with arguments 2 and photo. 2 stands for photo
    # removing.
    def removePhoto(self, photo):
        if photo in self.photos:
            photo.collectionID.remove(self.id)
            self.photos.remove(photo)
            for view in self.views:
                view.update(2, photo)

    # checks whether photo with id phid in photo list of the collection.
    # if exists show it nt using PIL library else print error.
    def fetchPhoto(self, phid):
        myimg = None
        for photo in self.photos:
            if phid == photo.id:
                myimg = photo
            break
        if myimg != None:
            myimg.img.show()
        else:
            print("There is no image with id:", phid)

    # This function creates photo list filtered with filters of the view. Adding photo list the view object.
    # Then, adding view object to the views list of the collection.
    def addView(self, view):
        newphotos = []  # create empty photo list
        # get the filters from the view object
        tagfilter, conj = view.getTagFilter()
        location = view.getLocationRect()
        time = view.getTimeInterval()
        for photo in self.photos:
            if conj:  # if conjunctive is true
                result =  all(elem in tagfilter  for elem in photo.tags)
                print("tagfilter:",tagfilter)
                print("phototags:",photo.tags)
                print(result)
                if result:  # tag filters of the view must be subset of photo's tags.
                    print("im in bro 1")
                    if isinrect(photo.location, location):  # check whether photo in the view's rectangle area.
                        print("im in bro2")
                        if time[0] <= photo.dateTime <= time[1]:  #check whether datetime of photo is in between of the view's time interval.
                            print("im in bro3")
                            newphotos.append(photo)  # if all conditions are true append photo the newphotos list.
            else:
                if any(x in tagfilter for x in photo.tags):  # checks if any of the tags are common.
                    if isinrect(photo.location, location):
                        if time[0] <= photo.dateTime <= time[1]:
                            newphotos.append(photo)  # if all conditions are true append photo the newphotos list.

        view.collectionID = self.id  # save the collection id in view object.
        view.photos = newphotos  # save filtered photos in view object.
        self.views.append(
            view)  # After making necessary operations for view, add view object to the views list of the collection.

    # add user to the sharedUsers list of the collection, and add collection to the user's collection list
    # Since share function in the view says that, "otherwise only users having access to collection can access the view,
    # we call view.share() function for every view in views list of the collection"
    def share(self, user):
        if(user not in self.sharedUsers):
            self.sharedUsers.append(user)
            user.collections.append(self)
            for view in self.views:
                view.share(user)
        else:
            print("The collection is already shared with the user with id:", user.id)

    # Remove user from the sharedUsers list of the collection, and remove collection from the user's collection list
    def unshare(self, user):
        if(user in self.sharedUsers):
            self.sharedUsers.remove(user)
            user.collections.remove(self)
        else:
            print("The collection is not shared with the user with id:", user.id)


class View:
    class_counter = 0  # keeps the id value for View class objects

    # View class objects have a name, tags list which is initially empty, conjunctive boolean initially false,
    # locationRect and timeInterval filters which are initially empty lists, sharedUsers list which holds initially
    # owner of the object, photos list that are match with the filters of view object, owner, collectionID which is
    # -1 since it is not assigned to any collection yet, and id to identify.
    def __init__(self, name, owner):
        self.name = name
        self.tags = []
        self.conj = False
        self.locationRect = []
        self.timeInterval = []
        self.sharedUsers = [owner]
        self.photos = []
        self.owner = owner
        owner.views.append(self)
        self.collectionID = -1
        self.id = View.class_counter
        View.class_counter += 1

    # Set tags list to given taglist and conj to given conj input if not specified then it is false.
    def setTagFilter(self, taglist, conj=False):
        self.tags = taglist
        self.conj = conj

    # Set locationRect list to given rectangle argument. Rectangle consists of list of 4 edge (long,latt) points,
    # starting from top left to bottom left in the clockwise direction.
    def setLocationRect(self, rectangle):
        self.locationRect = rectangle

    # Set timeInterval list to given start end datetimes.
    def setTimeInterval(self, start, end):
        self.timeInterval = [start, end]

    # Get the tags from tags list and conj
    def getTagFilter(self):
        return self.tags, self.conj

    # Get locationRect
    def getLocationRect(self):
        return self.locationRect

    # Get timeInterval
    def getTimeInterval(self):
        return self.timeInterval

    # Add given User to sharedUsers list of the view object and add view object to the views list of the given User.
    def share(self, user):
        if(user not in self.sharedUsers):
            self.sharedUsers.append(user)
            user.views.append(self)
        else:
            print("The view is already shared with the user with id:", user.id)
            

    # Remove given User from sharedUsers list of the view object and remove view object from the views list of the
    # given User.
    def unshare(self, user):
        if user in self.sharedUsers:
            self.sharedUsers.remove(user)
            user.views.remove(self)
        else:
            print("The view is not shared with the user with id:", user.id)

    # This function is called by collection when there is a modification in the collection object. If flag==1 it
    # means photo is added to collection else photo is removed from the collection If photo updated then,
    # it checks whether the added photo suits for the filters of the view object, if yes then photo is added to view
    # object's photo list. If photo removed then it removes the photo from the view object's photo list.
    def update(self, flag, photo):
        if (flag == 1):
            if self.conj:
                if set(self.tags).issubset(photo.tags):
                    if isinrect(photo.location, self.locationRect):
                        if self.timeInterval[0] <= photo.dateTime <= self.timeInterval[1]:
                            self.photos.append(photo)
                            print("View updated. Photo with id: ", photo.id, " is added to photo list of view with id:", self.id)
            else:
                if any(x in self.tags for x in photo.tags):
                    if isinrect(photo.location, self.locationRect):
                        if self.timeInterval[0] <= photo.dateTime <= self.timeInterval[1]:
                            self.photos.append(photo)
                            print("View updated. Photo with id: ", photo.id, " is added to photo list of view with id:", self.id)

        else:
            if photo in self.photos:
                self.photos.remove(photo)
                print("View updated. Photo with id: ", photo.id, " is removed from the photo list of view with id:",
                      self.id)

    # This function creates an empty id_list array to hold id's. Then, it appends the id's of the photos that are in
    # the photo list of the view object. Finally, return the id_list list.
    def photoList(self):
        id_list = []
        for photo in self.photos:
            id_list.append(photo.id)
        return id_list

    # Checks whether the photo with given photo id in view object's photo list.
    # If photo is found in list then show it by using PIL library, else print error.
    def fetchPhoto(self, phid):
        myimg = None
        for photo in self.photos:
            if phid == photo.id:
                myimg = photo
            break
        if myimg != None:
            myimg.img.show()
        else:
            print("There is no image with id:", phid, "in this view")


# Temporary User class for trying other classes and their functionalities. Objects of these class have a name,
# password which is "" for now, collections and views initially empty, and id to identify user.
class User:
    class_counter = 0

    def __init__(self, name):
        self.name = name
        self.password = ""
        self.collections = []
        self.views = []
        self.id = User.class_counter
        User.class_counter += 1


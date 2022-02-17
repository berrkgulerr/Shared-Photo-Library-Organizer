import cmd, sys
from phase1 import *

class Phase1Shell(cmd.Cmd):
    intro = 'Welcome to the Phase1Shell shell.   Type help or ? to list commands.\n'
    prompt = '(phase1) '
    file = None
    users = []
    collections = []
    views = []
    photos = []


    # ---- Inıtial Commands ----
    def do_createuser(self, arg):
        'Create user with the given name: createuser berk'
        args = arg.split(" ")
        if len(args) == 1:
            self.users.append(User(arg))
            print("User with id:", self.users[-1].id, " index:", len(self.users) - 1, "is created")
        else:
            print("ERROR: 1 argument should be given")

    def do_createphoto(self, arg):
        'Create user with the given path: createphoto 1.jpg'
        args = arg.split(" ")
        if len(args) == 1:
            self.photos.append(Photo(arg))
            print("Photo with id:", self.photos[-1].id, " index:", len(self.photos) - 1, "is created")
        else:
            print("ERROR: 1 argument should be given")

    # ---- Photo Commands ----
    def do_addtag(self, arg):
        'Add given tag to photo of given index: addtag 0 ankara (addtag index_photo tag)'
        args = arg.split(" ")
        print(args)
        if len(args) == 2:
            if len(self.photos) > int(args[0]):
                self.photos[int(args[0])].addTag(args[1])
                print("tag:", args[1], "is added to the photo with index", args[0])
            else:
                print("There is no photo with index", args[0])
        else:
            print("ERROR: 2 argument should be given")

    def do_removetag(self, arg):
        'Remove the given tag from the photo of given index: removetag 0 ankara (removetag index_photo tag)'
        args = arg.split(" ")
        if len(args) == 2:
            if len(self.photos) > int(args[0]):
                self.photos[int(args[0])].removeTag(args[1])
                print("tag:", args[1], "is removed from the photo with index", args[0])
            else:
                print("There is no photo with index", args[0])
        else:
            print("ERROR: 2 argument should be given")

    def do_setlocation(self, arg):
        'Set location to photo of given index: setlocation 0 20 35 (setlocation index_photo long latt)'
        args = arg.split(" ")
        if len(args) == 3:
            if len(self.photos) > int(args[0]):
                self.photos[int(args[0])].setLocation(float(args[1]), float(args[2]))
                print("location:(", args[1], "-", args[2], ") is added to the photo with index", args[0])
            else:
                print("There is no photo with index", args[0])
        else:
            print("ERROR: 3 argument should be given")

    def do_removelocation(self, arg):
        'Remove location info from the photo of given index: removelocation 0 (removelocation index_photo)'
        args = arg.split(" ")
        if len(args) == 1:
            if len(self.photos) > int(arg):
                self.photos[int(arg)].removeLocation()
                print("location of the photo with index", arg, "is removed.")
            else:
                print("There is no photo with index", arg)
        else:
            print("ERROR: 1 argument should be given")

    def do_setdatetime(self, arg):
        'Set date time to photo of given index: setdatetime 0 2007:10:14 16:27:13 (setdatetime index_photo datetime)'
        args = arg.split(" ")
        if len(args) == 3:
            if len(self.photos) > int(args[0]):
                self.photos[int(args[0])].setDateTime(args[1] + " " +args[2])
                print("datetime", args[1] + " " + args[2], "is added to the photo with index", args[0])
            else:
                print("There is no photo with index", args[0])
        else:
            print("ERROR: 3 argument should be given")


    # ---- Collection Commands ----
    def do_createcollection(self, arg):
        'Create collection with given name, and given index of owner user: createcollection mycol 0 (createcollection name index_use)' 
        args = arg.split(" ")
        if len(args) == 2:
            if len(self.users) >  int(args[1]):
                self.collections.append(Collection(args[0], self.users[int(args[1])]))
                print("Collection with id:",self.collections[-1].id, "and name:",self.collections[-1].name, "at index:", len(self.collections) - 1, "is created")
            else:
                print("There is no user with index", args[1])
        else:
            print("ERROR: 2 argument should be given")

    def do_addphoto(self, arg):
        'Add given index of photo to given index of collection: addphoto 0 0 (addphoto index_collection index_photo)'
        args = arg.split(" ")
        if len(args) == 2:
            if len(self.collections) > int(args[0]):
                if len(self.photos) > int(args[1]):
                    self.collections[int(args[0])].addPhoto(self.photos[int(args[1])])
                    print("Photo with index:", args[1], "is added to the collection with id:", args[0])
                else:
                    print("There is no photo with index", args[1])
            else:
                print("There is no collection with index", args[0])
        else:
            print("ERROR: 2 argument should be given")

    def do_removephoto(self, arg):
        'Remove given index of photo from the given index of collection: removephoto 0 0 (removephoto index_collection index_photo)'
        args = arg.split(" ")
        if len(args) == 2:
            if len(self.collections) > int(args[0]):
                if len(self.photos) > int(args[1]):    
                    self.collections[int(args[0])].removePhoto(self.photos[int(args[1])])
                    print("Photo with index:", args[1], "is removed from the collection with index:", args[0],".")
                else:
                    print("There is no photo with index", args[1])
            else:
                print("There is no collection with index", args[0])
        else:
            print("ERROR: 2 argument should be given")

    def do_collectionfetchphoto(self,arg):
        'Fetch and show the given index of photo from the given index of collection: collectionfetchphoto 0 1 (collectionfetchphoto index_collection index_photo)'
        args = arg.split(" ")
        if len(args) == 2:
            if len(self.collections) > int(args[0]):
                if len(self.photos) > int(args[1]):    
                    self.collections[int(args[0])].fetchPhoto(self.photos[int(args[1])].id)
                    print("Photo with index:", args[1]," is fetched from the collection with index:", args[0])
                else:
                    print("There is no photo with index", args[1])
            else:
                print("There is no collection with index", args[0])
        else:
            print("ERROR: 2 argument should be given")


    def do_addview(self, arg):
        'Add given index of view to given index of collection. addview 0 0 (addview index_collection index_view)'
        args = arg.split(" ")
        if len(args) == 2:
            if len(self.collections) > int(args[0]):
                if len(self.views) > int(args[1]):
                    self.collections[int(args[0])].addView(self.views[int(args[1])])
                    print("View with index: ", args[1]," is added to the collection with index:", args[0])
                else:
                    print("There is no view with index", args[1])
            else:
                print("There is no collection with index", args[0])
        else:
            print("ERROR: 2 argument should be given")

    def do_collectionshare(self, arg):
        'Share the collection with the user given collection index and user index: collectionshare 0 1 (collectionshare index_collection index_user)'
        args = arg.split(" ")
        if len(args) == 2:
            if len(self.collections) > int(args[0]):
                if len(self.users) > int(args[1]):
                    self.collections[int(args[0])].share(self.users[int(args[1])])
                    print("Collection with index:", args[0], "is shared with user id:", self.users[int(args[1])].id)
                else:
                    print("There is no user with index", args[1])
            else:
                print("There is no collection with index", args[0])
        else:
            print("ERROR: 2 argument should be given")

    def do_collectionunshare(self, arg):
        'Unshare the collection with the user given collection index and user index: collectionunshare 0 1 (collectionunshare index_collection index_user)'
        args = arg.split(" ")
        if len(args) == 2:
            if len(self.collections) > int(args[0]):
                if len(self.users) > int(args[1]):
                    self.collections[int(args[0])].unshare(self.users[int(args[1])])
                    print("Collection with id:", args[0], "is unshared with user id:", self.users[int(args[1])].id)
                else:
                    print("There is no user with index", args[1])
            else:
                print("There is no collection with index", args[0])
        else:
            print("ERROR: 2 argument should be given")


    # ---- View Commands ----
    def do_createview(self, arg):
        'Create view with the name and owner index of the view: createview myview 0'
        args = arg.split(" ")
        if len(args) == 2:
            if len(self.users) >  int(args[1]):
                self.views.append(View(args[0], self.users[int(args[1])]))
                print("View with id:",self.views[-1].id, "and name:",self.views[-1].name, "at index:", len(self.views) - 1, "is created")
            else:
                print("There is no user with index", args[1])
        else:
            print("ERROR: 2 argument should be given")

    def do_settagfilter(self, arg):
        'Set tag filter for the view index: 0 list_of_tags'
        args = arg.split()
        if len(args) == 3:
            if len(self.views) > int(args[0]):
                self.views[int(args[0])].setTagFilter(args[1], bool(args[2]))
                print("Tags", args[1], "are added and conjunctive is set to:", args[2], "to view with index:", args[0])
            else:
                print("There is no view with index", args[0])
        else:
            print("ERROR: 3 argument should be given")

    def do_setlocationrect(self, arg):
        'Set location of the region filtered with given index of view: 0 x1 y1 x2 y2 x3 y3 x4 y4'
        args = arg.split(" ")
        
        if len(args) == 9:
            if len(self.views) > int(args[0]):
                op1 = float(args[1]) 
                op2 = float(args[2]) 
                op3 = float(args[3]) 
                op4 = float(args[4]) 
                op5 = float(args[5]) 
                op6 = float(args[6]) 
                op7 = float(args[7]) 
                op8 = float(args[8]) 
                print([op1,op2,op3,op4])
                self.views[int(args[0])].setLocationRect([[op1,op2],[op3,op4],[op5,op6],[op7,op8]])
                print("Location rectangle", args[1], "is added to view with index:", args[0])
            else:
                print("There is no view with index", args[0])
        else:
            print("ERROR: 5 argument should be given")

    def do_settimeinterval(self, arg):
        'Set time interval information to the given view index: settimeinterval 0 start end'

        args = arg.split(" ")
        if len(args) == 5:
            if len(self.views) > int(args[0]):
                self.views[int(args[0])].setTimeInterval((args[1])+ " " +(args[2]) , args[3] + " " + args[4])
                print("Time interval", args[1], "is set to view with index:", args[0])
            else:
                print("There is no view with index", args[0])
        else:
            print("ERROR: 5 argument should be given")

    def do_gettagfilter(self, arg):
        'Get tag filter information the given view index: gettimeinterval 0'
        args = arg.split()
        if len(args) == 1:
            if len(self.views) > int(arg):
                a, b = self.views[int(arg)].getTagFilter()
                print("tags:", a, "conjunctive:", b)
            else:
                print("There is no view with index", arg)
        else:
            print("ERROR: 1 argument should be given")

    def do_getlocationrect(self, arg):
        'Get the region information the given view index: getlocationrect 0'
        args = arg.split()
        if len(args) == 1:
            if len(self.views) > int(arg):
                print(self.views[int(arg)].getLocationRect())
            else:
                print("There is no view with index", arg)
        else:
            print("ERROR: 1 argument should be given")

    def do_gettimeinterval(self, arg):
        'Get time interval information the given view index: gettimeinterval 0'
        args = arg.split()
        if len(args) == 1:
            if len(self.views) > int(arg):
                print(self.views[int(arg)].getTimeInterval())
            else:
                print("There is no view with index", arg)
        else:
            print("ERROR: 1 argument should be given")

    def do_viewshare(self, arg):
        'Share the view with the user given view index and user index: viewunshare 0 1 (viewshare index_view index_user)'
        args = arg.split(" ")
        if len(args) == 2:
            if len(self.views) > int(args[0]):
                if len(self.users) > int(args[1]):
                    self.views[int(args[0])].share(self.users[int(args[1])])
                    print("View with id:", args[0], "is shared with user id:", self.users[int(args[1])].id)
                else:
                    print("There is no user with index", args[1])
            else:
                print("There is no view with index", args[0])
        else:
            print("ERROR: 2 argument should be given")

    def do_viewunshare(self, arg):
        'Unshare the view with the user given view index and user index: viewunshare 0 1 (viewunshare index_view index_user)'
        args = arg.split(" ")
        if len(args) == 2:
            if len(self.views) > int(args[0]):
                if len(self.users) > int(args[1]):
                    self.views[int(args[0])].unshare(self.users[int(args[1])])
                    print("View with id:", args[0], "is unshared with user id:", self.users[int(args[1])].id)
                else:
                    print("There is no user with index", args[1])
            else:
                print("There is no view with index", args[0])
        else:
            print("ERROR: 2 argument should be given")

    def do_photolist(self, arg):
        'List the photos in the given view: photolist 0'
        args = arg.split()
        if len(args) == 1:
            if len(self.views) > int(arg):
                print(self.views[int(arg)].photoList())
            else:
                print("There is no view with index", arg)
        else:
            print("ERROR: 1 argument should be given")

    def do_viewfetchphoto(self, arg):
        'Display the photo in the specified view index with photo index: viewfetchphoto 0 1 (viewfetchphoto index_view index_photo)'
        args = arg.split(" ")
        if len(args) == 2:
            if len(self.views) > int(args[0]):
                if len(self.photos) > int(args[1]):
                    flag = False
                    for photo in self.views[int(arg[0])].photos:
                        if photo.id == int(args[1]):
                            flag = True
                    self.views[int(args[0])].fetchPhoto(self.photos[int(args[1])].id)
                    if flag:
                        print("Photo with id: ", args[1]," is fetched from the view with id:", args[0],".")
                else:
                    print("There is no photo with index", args[1])
            else:
                print("There is no view with index", args[0])
        else:
            print("ERROR: 2 argument should be given")

    def do_viewinfo(self, arg):
        'Show information about given view index: viewinfo 0'
        if len(self.views) > int(arg):
            print("Name:",self.views[int(arg)].name)
            print("Tags:",self.views[int(arg)].tags, self.views[int(arg)].conj)
            print("Location Rect:",self.views[int(arg)].locationRect)
            print("Time Interval:",self.views[int(arg)].timeInterval)
            print("Shared Users:",self.views[int(arg)].sharedUsers)
            print("Photos:",self.views[int(arg)].photos)
            print("Owner:",self.views[int(arg)].owner)
            print("Collection ID:",self.views[int(arg)].collectionID)
            print("ID:",self.views[int(arg)].id)
        else:
            print("There is no view with index", arg)

    def do_userinfo(self, arg):
        'Show information about given user index: userinfo 0'
        if len(self.users) > int(arg):
            print("Name:", self.users[int(arg)].name)
            print("Password:", self.users[int(arg)].password)
            print("Collections:", self.users[int(arg)].collections)
            print("Views:", self.users[int(arg)].views)
            print("ID:", self.users[int(arg)].id)
        else:
            print("There is no user with index", arg)

    def do_collectioninfo(self, arg):
        'Show information about given collection index: collectioninfo 0'
        if len(self.collections) > int(arg):
            print("Name:", self.collections[int(arg)].name)
            print("Photos:", self.collections[int(arg)].photos)
            print("Shared Users:", self.collections[int(arg)].sharedUsers)
            print("Views:", self.collections[int(arg)].views)
            print("Owner:", self.collections[int(arg)].owner)
            print("ID:", self.collections[int(arg)].id)
        else:
            print("There is no collection with index", arg)

    def do_photoinfo(self, arg):
        'Show information about given photo index: photoinfo 0'
        if len(self.photos) > int(arg):
            print("Location:", self.photos[int(arg)].location)
            print("Date Time:", self.photos[int(arg)].dateTime)
            print("Tags:", self.photos[int(arg)].tags)
            print("Collection IDs:", self.photos[int(arg)].collectionID)
            print("ID:", self.photos[int(arg)].id)
        else:
            print("There is no photo with index", arg)

    def do_bye(self, arg):
        'Stop recording, close the terminal, and exit:  BYE'
        print('Exiting.')
        sys.exit(0)
        return True
    # ----record and playback----
    def do_record(self, arg):
        'Save future commands to filename:  RECORD rose.cmd'
        self.file = open(arg, 'w')

    def do_playback(self, arg):
        'Playback commands from a file:  PLAYBACK rose.cmd'
        self.close()
        with open(arg) as f:
            self.cmdqueue.extend(f.read().splitlines())
            
    def precmd(self, line):
        line = line.lower()
        if self.file and 'playback' not in line:
            print(line, file=self.file)
        return line

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

if __name__ == '__main__':
    Phase1Shell().cmdloop()

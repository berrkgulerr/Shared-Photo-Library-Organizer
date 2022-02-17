import json
import random
import pymongo
from threading import *
from user import *
from helpers import *
from socket import *


class Agent(Thread):
    def __init__(self, ns, data_mutex):
        Thread.__init__(self)
        self.sock = ns
        self.lock = data_mutex
        self.users = []
        self.current_user = None
        users = users_table()
        cursor = users.find()
        user_list = list(cursor)
        for user in user_list:
            db_user = User(user['_id'], user['username'], user['password'], user['photo_ids'], user['collection_ids'], user['view_ids'])
            self.users.append(db_user)
        close_connection_to_db()

    def send_message(self, message):
        data = json.dumps({"command": "message", "message": message})
        self.sock.sendall(bytes(data, encoding="utf-8"))

    def send_notify(self, message):
        for client in self.clients:
            if client is not self.sock:
                data = json.dumps({"command": "notify", "notify": message})
                client.sendall(bytes(data, encoding="utf-8"))

    def register(self, req):
        not_valid = False
        with self.lock:
            for user in self.users:
                if req['username'] == user.username:
                    self.send_message("Invalid username.")
                    not_valid = True
                    break
            if not not_valid:
                user = User(id=None, username=req['username'], password=req['password'])
                self.users.append(user)
                self.current_user = user
                self.send_message("Successfully registered.")

    def login(self, req):
        with self.lock:
            userflag = False
            for user in self.users:
                if req['username'] == user.username and req['password'] == user.password:
                    self.send_message("Successfully login.")
                    self.current_user = user
                    userflag = True
                    break
            if (not userflag):
                self.send_message("Login failed!")

    def logout(self):
        self.current_user = None
        self.send_message("Successfully logout.")

    def createphoto(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.create_photo(req['path'])
            self.send_message(message)

    def addtag(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message ,notify= self.current_user.add_tag(int(req['photo_id']), req['tag'])
            self.send_message(message)

    def removetag(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.remove_tag(int(req['photo_id']), req['tag'])
            self.send_message(message)

    def setlocation(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.set_location(int(req['photo_id']), float(req['long']), float(req['latt']))
            self.send_message(message)

    def removelocation(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.remove_location(int(req['photo_id']))
            self.send_message(message)

    def setdatetime(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.set_date_time(int(req['photo_id']), req['date_time'])
            self.send_message(message)

    def createcollection(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.create_collection(req['collection_name'])
            self.send_message(message)

    def addphoto(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.add_photo(int(req['collection_id']), int(req['photo_id']))
            self.send_message(message)

    def removephoto(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.remove_photo(int(req['collection_id']), int(req['photo_id']))
            self.send_message(message)

    def collectionfetchphoto(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.collection_fetch_photo(int(req['collection_id']), int(req['photo_id']))
            self.send_message(message)

    def addview(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.add_view(int(req['collection_id']), int(req['view_id']))
            self.send_message(message)

    def collectionshare(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            user_flag = False
            for user in self.users:
                if user.id == int(req['user_id']):
                    message = self.current_user.collection_share(int(req['collection_id']), user.id)
                    self.send_message(message)
                    user_flag = True
                    break
            if(not user_flag):
                message = str("There is no user with given id.")
                self.send_message(message)

    def collectionunshare(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            user_flag = False
            for user in self.users:
                if user.id == int(req['user_id']):
                    message = self.current_user.collection_unshare(int(req['collection_id']), user.id)
                    self.send_message(message)
                    user_flag = True
                    break
            if(not user_flag):
                message = str("There is no user with given id.")
                self.send_message(message)

    def createview(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.create_view(req['view_name'])
            self.send_message(message)

    def settagfilter(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.set_tag_filter(int(req['view_id']), req['tag_list'],req['conj'] )
            self.send_message(message)

    def setlocationrect(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.set_location_rect(int(req['view_id']), list(req['rectangle']))
            self.send_message(message)

    def settimeinterval(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.set_time_interval(int(req['view_id']), req['start'], req['end'])
            self.send_message(message)

    def gettagfilter(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.get_tag_filter(int(req['view_id']))
            self.send_message(str(message))

    def getlocationrect(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.get_location_rect(int(req['view_id']))
            self.send_message(str(message))

    def gettimeinterval(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.get_time_interval(int(req['view_id']))
            self.send_message(str(message))

    def viewshare(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            user_flag = False
            for user in self.users:
                if user.id == int(req['user_id']):
                    message = self.current_user.view_share(int(req['view_id']), user.id)
                    self.send_message(message)
                    user_flag = True
                    break
            if(not user_flag):
                message = str("There is no user with given id.")
                self.send_message(message)

    def viewunshare(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            user_flag = False
            for user in self.users:
                if user.id == int(req['user_id']):
                    message = self.current_user.view_unshare(int(req['view_id']), user.id)
                    self.send_message(message)
                    user_flag = True
                    break
            if(not user_flag):
                message = str("There is no user with given id.")
                self.send_message(message)

    def viewupdate(self, req):
        pass

    def photolist(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.photo_list(int(req['view_id']))
            self.send_message(message)

    def viewfetchphoto(self, req):
        with self.lock:
            users = users_table()
            updated_user = users.find_one({'_id':self.current_user.id})
            self.current_user = User(updated_user['_id'],updated_user['username'], updated_user['password'], updated_user['photo_ids'],updated_user['collection_ids'], updated_user['view_ids'])
            close_connection_to_db()
            message = self.current_user.view_fetch_photo(int(req['view_id']), int(req['photo_id']))
            self.send_message(message)

    def run(self):
        try:
            while True:
                req = json.loads(self.sock.recv(4096))
                print(req)
                if req["command"] == "register":
                    self.register(req)
                elif req["command"] == "login":
                    self.login(req)
                elif req["command"] == "userinfo":
                    self.userinfo(req)
                elif req["command"] == "photoinfo":
                    self.photoinfo(req)
                elif req["command"] == "collectioninfo":
                    self.userinfo(req)
                elif req["command"] == "collectioninfo":
                    self.photoinfo(req)
                elif req["command"] == "createphoto":
                    self.createphoto(req)
                elif req["command"] == "addtag":
                    self.addtag(req)
                elif req["command"] == "removetag":
                    self.removetag(req)
                elif req["command"] == "setlocation":
                    self.setlocation(req)
                elif req["command"] == "removelocation":
                    self.removelocation(req)
                elif req["command"] == "setdatetime":
                    self.setdatetime(req)
                elif req["command"] == "createcollection":
                    self.createcollection(req)
                elif req["command"] == "addphoto":
                    self.addphoto(req)
                elif req["command"] == "removephoto":
                    self.removephoto(req)
                elif req["command"] == "collectionfetchphoto":
                    self.collectionfetchphoto(req)
                elif req["command"] == "addview":
                    self.addview(req)
                elif req["command"] == "collectionshare":
                    self.collectionshare(req)
                elif req["command"] == "collectionunshare":
                    self.collectionunshare(req)
                elif req["command"] == "createview":
                    self.createview(req)
                elif req["command"] == "settagfilter":
                    self.settagfilter(req)
                elif req["command"] == "setlocationrect":
                    self.setlocationrect(req)
                elif req["command"] == "settimeinterval":
                    self.settimeinterval(req)
                elif req["command"] == "gettagfilter":
                    self.gettagfilter(req)
                elif req["command"] == "getlocationrect":
                    self.getlocationrect(req)
                elif req["command"] == "gettimeinterval":
                    self.gettimeinterval(req)
                elif req["command"] == "viewshare":
                    self.viewshare(req)
                elif req["command"] == "viewunshare":
                    self.viewunshare(req)
                elif req["command"] == "photolist":
                    self.photolist(req)
                elif req["command"] == "viewfetchphoto":
                    self.viewfetchphoto(req)
        except KeyboardInterrupt:
            print("Closing...")
            return

def server(port):
    data_mutex = Lock()
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('',port))
    s.listen(10)    # 1 is queue size for "not yet accept()'ed connections"
    print("server ready..! port {}".format(port))
    try:
        #while True:
        while True:    # just limit # of accepts for Thread to exit
            ns, peer = s.accept()
            print(peer, "connected")
            t = Agent(ns,data_mutex,)
            t.start()
            # now main thread ready to accept next connection
    except:
        s.close()
    finally:
        s.close()

if __name__ == "__main__":
    port = random.randint(1024, 49151)
    with open("port.txt", "w") as f:
        f.write(str(port))
    server(port)

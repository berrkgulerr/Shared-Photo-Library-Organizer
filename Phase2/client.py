from threading import *
from socket import *
import json
import os
import subprocess
import sys
from PIL import Image as PILIMAGE
# server ip's
SERVER_IP = '127.0.0.1'

def client():

    s = socket(AF_INET, SOCK_STREAM)

    with open("port.txt", "r") as f:
        port = int(f.readline())

    s.connect((SERVER_IP, port))
    while True:
        try:
            req = input("Send request:")
        except Exception as e:
            # EOF error
            break
        req = json.loads(req)
        if req["command"] == "logout":
            print("Successfully logged out.")
            s.close()
            break
        # data to be sent
        senddata = json.dumps(req)
        s.sendall(bytes(senddata,encoding="utf-8"))
        res = json.loads(s.recv(4096))

        if req["command"] == "collectionfetchphoto" or req["command"] == "viewfetchphoto":
            if res['message'] == "temp.jpg":
                print("Given photo is fetched")
                process = subprocess.Popen(['eog', res['message']])
                process.wait()
                os.remove("temp.jpg")
            else:
                print ("Received Response:\n", res['message'])
        else:
            print ("Received Response:\n", res['message'])

    # close the socket
    s.close()

if __name__ == '__main__':
    client()

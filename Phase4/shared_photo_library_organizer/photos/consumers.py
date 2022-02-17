from channels.generic.websocket import WebsocketConsumer
import json


class SockConsumer(WebsocketConsumer):
    waiters = {}

    def connect(self):
        print("connected")
        self.accept()

    def disconnect(self, close_code):
        print("disconnected")
        pass

    def receive(self, text_data=None, binary_data=None):
        msg = json.loads(text_data)

        if msg["op"] == "socket_open":
            SockConsumer.waiters[msg["user_id"]] = self
        self.send(text_data=json.dumps({"msg": "msmsmsmsmmsms"}))

    @classmethod
    def broadcast(cls, users, msg):
        for user in users:
            SockConsumer.waiters[str(user)].send(text_data=json.dumps(msg))

    @classmethod
    def send_notification(cls, users, msg):
        for user in users:
            SockConsumer.waiters[str(user)].send(text_data=json.dumps(msg))

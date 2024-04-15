import json
from channels.generic.websocket import AsyncWebsocketConsumer

from django.utils.functional import LazyObject


# Custom LazyObject subclass
class CustomLazyObject(LazyObject):
    def _setup(self):
        raise RuntimeError("Accessing scope user before it is ready")


active_users = {}


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['user'].username
        active_users[self.user_id] = self.channel_name
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the user's WebSocket connection from the active users mapping
        del active_users[self.user_id]

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        time = text_data_json["time"]

        receiver_user_id = text_data_json['receiver_user_id']  # ID of the user to send the message to

        receiver_channel_name = active_users.get(receiver_user_id)
        sender_channel_name = active_users.get(username)
        if receiver_channel_name:
            # Send the message directly to the receiver's WebSocket connection
            await self.channel_layer.send(
                receiver_channel_name,
                {
                    "type": "sendMessage",
                    "message": message,
                    "username": username,
                    "time": time,
                    'receiver_user_id': receiver_user_id,
                    'msg_type': 'R',
                }
            )
            if sender_channel_name:
                await self.channel_layer.send(
                    sender_channel_name,
                    {
                        "type": "sendMessage",
                        "message": message,
                        "username": username,
                        "time": time,
                        'receiver_user_id': receiver_user_id,
                        'msg_type': 'S',
                    }
                )
        else:
            # Handle case where the receiver is not found or offline
            await self.send(text_data=json.dumps({
                'error': 'Receiver not found or offline',
            }))

    async def sendMessage(self, event):
        message = event["message"]
        username = event["username"]
        time = event["time"]
        receiver_user_id = event["receiver_user_id"]
        msg_type = event["msg_type"]
        await self.send(text_data=json.dumps(
            {"message": message, "username": username, "time": time, 'receiver_user_id': receiver_user_id,
             'msg_type': msg_type}))

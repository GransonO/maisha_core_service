import datetime

import bugsnag
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from maisha_service.apps.core.models import MaishaChats
from maisha_service.apps.core.serializers import CoreChatsSerializer


class SocketChat(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        print("text_data *** ----------- {}".format(text_data))
        print("text_data *** ----------- {}".format(type(text_data)))
        chat_data = json.loads(text_data)
        print("chat_data ----------- {}".format(type(chat_data)))
        print("chat_data ----------- {}".format(chat_data["message"]))

        # Send message to room group
        # chat_result = await self.persist_to_db(chat_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': text_data
                # 'message': chat_result
            }
        )

    @staticmethod
    def default_converter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message, default=str))

    @database_sync_to_async
    def persist_to_db(self, passed_data):
        # New message posted
        try:
            serializer = CoreChatsSerializer(
                data=passed_data, partial=True
            )
            serializer.is_valid()
            serializer.save()

            chats = MaishaChats.objects.filter(session_id=passed_data["session_id"])
            the_chats = CoreChatsSerializer(instance=chats, many=True)

            return {
                    "data": list(the_chats.data),
                    "success": True,
                    "message": "Posted successfully"
                }
        except Exception as E:
            bugsnag.notify(
                Exception('CoreChat Post: {}'.format(E))
            )
            return {
                    "success": False,
                    "message": "Posting failed"
                }

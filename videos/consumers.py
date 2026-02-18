from channels.generic.websocket import AsyncWebsocketConsumer
import json

class LiveConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']  # ✅ FIXED
        self.room_group_name = f'live_{self.room_name}'

        print("WebSocket CONNECTED:", self.room_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        print("📥 RECEIVED FROM CLIENT:", data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_signal',
                'message': data,
                'sender_channel_name': self.channel_name
            }
        )

    async def send_signal(self, event):

        print("📡 SENDING TO GROUP:", event)

        if self.channel_name == event['sender_channel_name']:
            return

        await self.send(text_data=json.dumps(event['message']))

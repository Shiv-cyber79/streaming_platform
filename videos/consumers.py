from channels.generic.websocket import AsyncWebsocketConsumer
import json

# 🔥 NEW: store viewers per room
room_viewers = {}

class LiveConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'live_{self.room_name}'

        print("WebSocket CONNECTED:", self.room_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # ✅ ADD VIEWER
        if self.room_name not in room_viewers:
            room_viewers[self.room_name] = set()

        room_viewers[self.room_name].add(self.channel_name)

        print("👤 User joined:", self.channel_name)

        # 🔥 SEND UPDATED COUNT
        await self.send_viewer_count()


    async def disconnect(self, close_code):

        # ✅ REMOVE VIEWER
        if self.room_name in room_viewers:
            room_viewers[self.room_name].discard(self.channel_name)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        print("❌ User left:", self.channel_name)

        # 🔥 UPDATE COUNT
        await self.send_viewer_count()


    async def receive(self, text_data):
       data = json.loads(text_data)

       print("📥 RECEIVED FROM CLIENT:", data)

    # Send WebRTC signal
       await self.channel_layer.group_send(
           self.room_group_name,
           {
                'type': 'send_signal',
                'message': data,
                'sender_channel_name': self.channel_name
           }
       )

       if data.get("chat"):
          await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': data['chat']
            }
        )
          
    async def chat_message(self, event):
       await self.send(text_data=json.dumps({
           "chat": event["message"]
       }))

    async def send_signal(self, event):

        print("📡 SENDING TO GROUP:", event)

        # ❌ DON'T SEND BACK TO SENDER
        if self.channel_name == event['sender_channel_name']:
            return

        await self.send(text_data=json.dumps(event['message']))


    # 🔥 NEW FUNCTION
    async def send_viewer_count(self):
        count = len(room_viewers.get(self.room_name, []))

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "viewer_update",
                "count": count
            }
        )


    # 🔥 HANDLE VIEWER UPDATE
    async def viewer_update(self, event):
        await self.send(text_data=json.dumps({
            "viewers": event["count"]
        }))
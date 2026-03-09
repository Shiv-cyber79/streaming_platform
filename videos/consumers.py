from channels.generic.websocket import AsyncWebsocketConsumer
from .models import LiveStream
from channels.db import database_sync_to_async
import json

room_viewers = {}

class LiveConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name       = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'live_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        if self.room_name not in room_viewers:
            room_viewers[self.room_name] = set()
        room_viewers[self.room_name].add(self.channel_name)

        print(f"✅ CONNECTED: {self.channel_name} → room:{self.room_name}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type":   "user_status",
                "status": "online",
                "user":   self.channel_name,
                "sender": self.channel_name,
            }
        )
        await self.send_viewer_count()

    async def disconnect(self, close_code):
        if self.room_name in room_viewers:
            room_viewers[self.room_name].discard(self.channel_name)

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"❌ DISCONNECTED: {self.channel_name}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type":   "user_status",
                "status": "offline",
                "user":   self.channel_name,
                "sender": self.channel_name,
            }
        )
        await self.send_viewer_count()

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"📥 FROM {self.channel_name[-8:]}:", data)

        # ✅ PRIORITY 1: CHAT (FIXED)
        if "chat" in data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_broadcast",
                    "chat": data["chat"],
                    "sender": data.get("sender", "Anonymous"),
                }
            )
            return

    # ── Direct WebRTC signal ──
        if "target" in data:
            target_channel = data.pop("target")
            await self.channel_layer.send(
                target_channel,
                {
                    "type": "direct_signal",
                    "message": data,
                    "sender_channel_name": self.channel_name,
                }
            )
            return

    # ── Viewer ready ──
        if data.get("type") == "viewer_ready":
            await self.channel_layer.group_send(
               self.room_group_name,
               {
                   "type": "viewer_ready_msg",
                   "sender_channel_name": self.channel_name,
                }
            )
            return

    # ── Stream started ──
        if data.get("type") == "stream_started":
           await self.channel_layer.group_send(
               self.room_group_name,
               {
                   "type": "stream_started_msg",
                   "sender_channel_name": self.channel_name,
               }
           )
           return

        if data.get("type") == "stream_ended":
           room = self.room_name   # usually already defined in consumer
    
           await database_sync_to_async(
               LiveStream.objects.filter(room_name=room).update
           )(is_live=False)

           await self.channel_layer.group_send(
               self.room_group_name,
               {
                   "type": "stream_ended_msg",
                   "sender_channel_name": self.channel_name,
               }
           )
           return
    
    async def chat_broadcast(self, event):
       await self.send(text_data=json.dumps({
          "chat": event["chat"],
          "sender": event["sender"],
       }))
        
    async def chat_message(self, event):
       await self.send(text_data=json.dumps({
           "chat": event["chat"],
           "sender": event["sender"],
        }))   
        
    async def stream_ended_msg(self, event):
       await self.send(text_data=json.dumps({
           "type": "stream_ended"
       }))
        
    async def direct_signal(self, event):
        msg = event["message"]
        msg["sender_channel_name"] = event["sender_channel_name"]
        await self.send(text_data=json.dumps(msg))

    async def chat_broadcast(self, event):
        await self.send(text_data=json.dumps({
            "chat":   event["chat"],
            "sender": event["sender"],
        }))

    async def viewer_ready_msg(self, event):
        # Only send to broadcaster (not back to the viewer who sent it)
        if self.channel_name == event["sender_channel_name"]:
            return
        await self.send(text_data=json.dumps({
            "type":                "viewer_ready",
            "sender_channel_name": event["sender_channel_name"],
        }))

    async def stream_started_msg(self, event):
        # Only send to viewers (not back to broadcaster)
        if self.channel_name == event["sender_channel_name"]:
            return
        await self.send(text_data=json.dumps({
            "type": "stream_started",
        }))

    async def send_viewer_count(self):
        count = len(room_viewers.get(self.room_name, set()))
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "viewer_update", "count": count}
        )

    async def viewer_update(self, event):
        await self.send(text_data=json.dumps({"viewers": event["count"]}))

    async def user_status(self, event):
        if self.channel_name == event.get("sender"):
            return
        await self.send(text_data=json.dumps({
            "type":   "status",
            "user":   event["user"],
            "status": event["status"],
        }))
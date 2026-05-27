# polls/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Poll
from .services import PollService

class PollConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.poll_id = self.scope['url_route']['kwargs']['poll_id']
        self.room_group_name = f'poll_{self.poll_id}'

        # 检查认证（简单示例：拒绝未登录用户）
       # if self.scope['user'].is_anonymous:
        #    await self.close()
        #    return
        
        # 检查投票是否存在
        poll_exists = await self.poll_exists(self.poll_id)
        if not poll_exists:
            await self.close()
            return
        
        # 加入房间
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        # 离开房间
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # 接收来自前端消息（例如客户端要求刷新，暂不使用）
    async def receive(self, text_data):
        pass
    
    # 处理来自 group 的 vote_update 消息
    async def vote_update(self, event):
        # 直接转发给 WebSocket
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'payload': event['payload']
        }))
    
    @database_sync_to_async
    def poll_exists(self, poll_id):
        return Poll.objects.filter(pk=poll_id).exists()
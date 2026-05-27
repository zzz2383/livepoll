# polls/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import Poll

User = get_user_model()

class PollConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.poll_id = self.scope['url_route']['kwargs']['poll_id']
        self.room_group_name = f'poll_{self.poll_id}'

        # 从 URL 查询参数中获取 token
        query_string = self.scope['query_string'].decode()
        params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
        token = params.get('token', None)

        # 验证 token 并获取用户
        if not token:
            await self.close()
            return

        user = await self.get_user_from_token(token)
        if not user:
            await self.close()
            return

        self.scope['user'] = user

        # 检查投票是否存在
        poll_exists = await self.poll_exists(self.poll_id)
        if not poll_exists:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def vote_update(self, event):
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'payload': event['payload']
        }))

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None

    @database_sync_to_async
    def poll_exists(self, poll_id):
        return Poll.objects.filter(pk=poll_id).exists()
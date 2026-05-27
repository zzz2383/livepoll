# polls/infrastructure/message_sender.py
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class MessageSender:
    """封装向 Channels group 发送消息的逻辑"""
    
    def send_vote_update(self, poll_id: int, option_id: int, new_count: int, total_votes: int):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'poll_{poll_id}',
            {
                'type': 'vote_update',
                'payload': {
                    'poll_id': poll_id,
                    'option_id': option_id,
                    'new_count': new_count,
                    'total_votes': total_votes
                }
            }
        )
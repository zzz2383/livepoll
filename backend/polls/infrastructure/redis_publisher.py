# polls/infrastructure/redis_publisher.py
import redis
import json

class RedisPublisher:
    """封装 Redis 发布功能，用于实时推送投票更新"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host='127.0.0.1', port=6379, db=0, decode_responses=True
        )
    
    def publish_vote_update(self, poll_id: int, option_id: int, new_count: int, total_votes: int):
        message = json.dumps({
            'type': 'vote_update',
            'payload': {
                'poll_id': poll_id,
                'option_id': option_id,
                'new_count': new_count,
                'total_votes': total_votes
            }
        })
        self.redis_client.publish(f'poll_{poll_id}', message)
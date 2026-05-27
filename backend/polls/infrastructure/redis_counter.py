# polls/infrastructure/redis_counter.py
import redis
from django.conf import settings

class RedisVoteCounter:
    """封装 Redis 原子计数操作，作为缓存层"""
    
    def __init__(self):
        # 使用 Django 的 Redis 缓存连接（或直接连接）
        self.redis_client = redis.Redis(
            host='127.0.0.1', port=6379, db=0, decode_responses=True
        )
    
    def incr(self, poll_id: int, option_id: int) -> int:
        key = f"vote:{poll_id}:option:{option_id}"
        return self.redis_client.incr(key)
    
    def get_counts(self, poll_id: int, option_ids: list[int]) -> dict[int, int]:
        pipe = self.redis_client.pipeline()
        for oid in option_ids:
            key = f"vote:{poll_id}:option:{oid}"
            pipe.get(key)
        results = pipe.execute()
        counts = {}
        for oid, val in zip(option_ids, results):
            counts[oid] = int(val) if val else 0
        return counts
    
    def sync_to_db(self, poll_id: int, option_counts: dict[int, int]):
        """将 Redis 计数写回 SQLite（可选定期任务）"""
        from polls.models import Option
        for oid, count in option_counts.items():
            Option.objects.filter(pk=oid).update(vote_count=count)
# polls/services.py
from django.utils import timezone 
from .models import Poll
from .repositories import PollRepository, VoteRepository
from .infrastructure.redis_counter import RedisVoteCounter
from .infrastructure.message_sender import MessageSender
from django.core.exceptions import PermissionDenied

class PollService:
    def __init__(self):
        self.poll_repo = PollRepository()
        self.vote_repo = VoteRepository()
        self.counter = RedisVoteCounter()
        self.sender = MessageSender()

    def create_poll(self, user, title: str, options: list[str], 
                    is_multiple: bool = False, closes_at=None) -> dict:
        poll = self.poll_repo.create_poll(title, options, user, is_multiple, closes_at)
        return self._poll_to_dict(poll)

    def get_poll_detail(self, poll_id: int, user=None) -> dict:
        poll = self.poll_repo.get_poll_by_id(poll_id)
        return self._poll_to_dict(poll, user)

    def vote(self, user, poll_id: int, option_ids: list[int]) -> dict:
        poll = self.poll_repo.get_poll_by_id(poll_id)
        if poll.is_closed():
            raise PermissionDenied("Poll has closed")
        if self.vote_repo.has_voted(user, poll):
            raise PermissionDenied("You have already voted in this poll")
        valid_option_ids = set(poll.options.values_list('id', flat=True))
        for oid in option_ids:
            if oid not in valid_option_ids:
                raise ValueError(f"Option {oid} does not belong to this poll")
        
        # 1. 持久化投票记录到 SQLite（防重）
        self.vote_repo.record_vote(user, poll, option_ids)
        
        # 2. Redis 原子递增并推送实时消息
        for oid in option_ids:
            new_count = self.counter.incr(poll_id, oid)
            # 通过 MessageSender 向 Channels group 发送消息
            self.sender.send_vote_update(poll_id, oid, new_count, None)
        
        # 3. 返回更新后的投票详情（从 Redis 读取最新计数）
        return self.get_poll_detail(poll_id, user)

    def list_my_polls(self, user) -> list[dict]:
        polls = self.poll_repo.list_polls_by_user(user)
        return [self._poll_to_dict(p) for p in polls]

    def _poll_to_dict(self, poll: Poll, user=None) -> dict:
        has_voted = False
        if user and user.is_authenticated:
            has_voted = self.vote_repo.has_voted(user, poll)
        options_qs = poll.options.all()
        option_ids = [opt.id for opt in options_qs]
        redis_counts = self.counter.get_counts(poll.id, option_ids)
        options = []
        total_votes = 0
        for opt in options_qs:
            count = redis_counts.get(opt.id, opt.vote_count)
            options.append({
                'id': opt.id,
                'text': opt.text,
                'count': count
            })
            total_votes += count
        return {
            'id': poll.id,
            'title': poll.title,
            'options': options,
            'is_multiple': poll.is_multiple,
            'closes_at': poll.closes_at.isoformat() if poll.closes_at else None,
            'created_by': poll.created_by.username,
            'total_votes': total_votes,
            'is_closed': poll.is_closed(),
            'created_at': poll.created_at.isoformat(),
            'has_voted': has_voted
        }
    
    def close_expired_polls(self):
        now = timezone.now()
        expired_polls = self.poll_repo.get_expired_open_polls(now)
        for poll in expired_polls:
            self.poll_repo.close_poll(poll)
            # 通过 WebSocket 通知所有监听者投票已关闭
        self.sender.send_poll_closed(poll.id)

    def list_participated_polls(self, user) -> list[dict]:
        polls = self.vote_repo.get_participated_polls(user)
        return [self._poll_to_dict(p) for p in polls]

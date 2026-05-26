# polls/services.py
from .models import Poll

from .repositories import PollRepository, VoteRepository
from django.core.exceptions import PermissionDenied

class PollService:
    def __init__(self):
        self.poll_repo = PollRepository()
        self.vote_repo = VoteRepository()

    def create_poll(self, user, title: str, options: list[str], 
                    is_multiple: bool = False, closes_at=None) -> dict:
        """
        返回值与接口层约定的字典，包含 Poll 信息
        """
        poll = self.poll_repo.create_poll(title, options, user, is_multiple, closes_at)
        return self._poll_to_dict(poll)

    def get_poll_detail(self, poll_id: int) -> dict:
        poll = self.poll_repo.get_poll_by_id(poll_id)
        return self._poll_to_dict(poll)

    def vote(self, user, poll_id: int, option_ids: list[int]) -> dict:
        poll = self.poll_repo.get_poll_by_id(poll_id)
        if poll.is_closed():
            raise PermissionDenied("Poll has closed")
        if self.vote_repo.has_voted(user, poll):
            raise PermissionDenied("You have already voted in this poll")
        # 校验选项是否属于该投票
        valid_option_ids = set(poll.options.values_list('id', flat=True))
        for oid in option_ids:
            if oid not in valid_option_ids:
                raise ValueError(f"Option {oid} does not belong to this poll")
        self.vote_repo.record_vote(user, poll, option_ids)
        # 返回更新后的投票详情
        return self.get_poll_detail(poll_id)

    def list_my_polls(self, user) -> list[dict]:
        polls = self.poll_repo.list_polls_by_user(user)
        return [self._poll_to_dict(p) for p in polls]

    def _poll_to_dict(self, poll: Poll) -> dict: 
        options = []
        for opt in poll.options.all():
            options.append({
                'id': opt.id,
                'text': opt.text,
                'count': opt.vote_count
            })
        return {
            'id': poll.id,
            'title': poll.title,
            'options': options,
            'is_multiple': poll.is_multiple,
            'closes_at': poll.closes_at.isoformat() if poll.closes_at else None,
            'created_by': poll.created_by.username,
            'total_votes': sum(o.vote_count for o in poll.options.all()),
            'is_closed': poll.is_closed(),
            'created_at': poll.created_at.isoformat()
        }
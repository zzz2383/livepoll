# polls/repositories.py
from django.db import transaction
from .models import Poll, Option, VoteRecord

class PollRepository:
    def create_poll(self, title: str, options_text: list[str], created_by, 
                    is_multiple: bool = False, closes_at=None) -> Poll:
        with transaction.atomic():
            poll = Poll.objects.create(
                title=title,
                is_multiple=is_multiple,
                closes_at=closes_at,
                created_by=created_by
            )
            for text in options_text:
                Option.objects.create(poll=poll, text=text)
            return poll

    def get_poll_by_id(self, poll_id: int) -> Poll:
        return Poll.objects.select_related('created_by').prefetch_related('options').get(pk=poll_id)

    def list_polls_by_user(self, user) -> list[Poll]:
        return Poll.objects.filter(created_by=user).order_by('-created_at')

    def delete_poll(self, poll: Poll):
        poll.delete()

    def get_expired_open_polls(self, now):
        return Poll.objects.filter(closes_at__lte=now, closed=False)

    def close_poll(self, poll):
        poll.closed = True
        poll.save()

class VoteRepository:
    def has_voted(self, user, poll) -> bool:
        return VoteRecord.objects.filter(user=user, poll=poll).exists()

    def record_vote(self, user, poll, option_ids: list[int]):
        with transaction.atomic():
            for oid in option_ids:
                option = Option.objects.get(pk=oid, poll=poll)
                VoteRecord.objects.create(user=user, poll=poll, option=option)
                # 不再增加 vote_count 字段，该字段由 Redis 定期同步或直接从 Redis 读取

    def get_option_counts(self, poll: Poll) -> dict[int, int]:
        """获取各选项当前票数（从 SQLite 读取）"""
        return {opt.id: opt.vote_count for opt in poll.options.all()}
    
    def get_participated_polls(self, user):
        voted_poll_ids = VoteRecord.objects.filter(user=user).values_list('poll_id', flat=True).distinct()
        # 按最近投票时间排序，可以用 Poll.created_at 或 VoteRecord.voted_at
        polls = Poll.objects.filter(id__in=voted_poll_ids).order_by('-created_at')
        return polls
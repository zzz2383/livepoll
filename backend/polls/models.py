# polls/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Poll(models.Model):
    title = models.CharField(max_length=200)
    is_multiple = models.BooleanField(default=False)  # 是否多选
    closes_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polls')
    created_at = models.DateTimeField(auto_now_add=True)

    def is_closed(self):
        if self.closes_at:
            from django.utils import timezone
            return timezone.now() >= self.closes_at
        return False

class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    # vote_count 冗余字段，用于快速查询，后期可与 Redis 同步
    vote_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['id']  # 保持选项顺序

class VoteRecord(models.Model):
    """记录谁在哪个投票中投了哪些选项（用于防重复投票）"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poll', 'option')  # 同一用户对同一选项只能投一次
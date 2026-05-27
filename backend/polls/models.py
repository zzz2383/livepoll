# polls/models.py
from django.db import models
from django.conf import settings  # 导入 settings

class Poll(models.Model):
    title = models.CharField(max_length=200)
    is_multiple = models.BooleanField(default=False)
    closes_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 使用字符串，延迟加载
        on_delete=models.CASCADE,
        related_name='polls'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def is_closed(self):
        if self.closes_at:
            from django.utils import timezone
            return timezone.now() >= self.closes_at
        return False

class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    vote_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['id']

class VoteRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poll', 'option')
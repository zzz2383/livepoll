from django.test import TestCase
from django.contrib.auth import get_user_model
from polls.services import PollService
from unittest.mock import patch, MagicMock
from django.core.exceptions import PermissionDenied

User = get_user_model()

class PollServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # 模拟 Redis 计数器和消息发送器
        self.counter_patcher = patch('polls.services.RedisVoteCounter')
        self.sender_patcher = patch('polls.services.MessageSender')
        self.mock_counter = self.counter_patcher.start()
        self.mock_sender = self.sender_patcher.start()
        self.addCleanup(self.counter_patcher.stop)
        self.addCleanup(self.sender_patcher.stop)
        
        self.service = PollService()
    
    def test_vote_uses_redis(self):
        poll = self.service.create_poll(self.user, 'Test', ['A', 'B'])
        # 模拟 Redis incr 返回 1
        self.mock_counter.return_value.incr.return_value = 1
        result = self.service.vote(self.user, poll['id'], [poll['options'][0]['id']])
        # 断言调用了 incr 和 send_vote_update
        self.mock_counter.return_value.incr.assert_called()
        self.mock_sender.return_value.send_vote_update.assert_called()
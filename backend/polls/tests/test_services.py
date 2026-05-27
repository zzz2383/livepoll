# polls/tests/test_services.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from unittest.mock import patch, MagicMock

from polls.services import PollService

User = get_user_model()

class PollServiceTest(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(username='polltester', password='testpass')
        self.other_user = User.objects.create_user(username='other', password='testpass')
        
        # Mock RedisVoteCounter 和 MessageSender
        self.counter_patcher = patch('polls.services.RedisVoteCounter')
        self.sender_patcher = patch('polls.services.MessageSender')
        self.mock_counter_cls = self.counter_patcher.start()
        self.mock_sender_cls = self.sender_patcher.start()
        
        # 配置 Mock 实例的行为
        self.mock_counter = MagicMock()
        self.mock_counter.get_counts.return_value = {}  # 默认没有 Redis 计数，回退到 DB vote_count
        self.mock_counter.incr.return_value = 1
        self.mock_counter_cls.return_value = self.mock_counter
        
        self.mock_sender = MagicMock()
        self.mock_sender_cls.return_value = self.mock_sender
        
        self.service = PollService()
        self.addCleanup(self.counter_patcher.stop)
        self.addCleanup(self.sender_patcher.stop)
    
    def test_create_poll(self):
        result = self.service.create_poll(
            self.user, 
            title='Test Poll', 
            options=['A', 'B', 'C'],
            is_multiple=False
        )
        self.assertEqual(result['title'], 'Test Poll')
        self.assertEqual(len(result['options']), 3)
        self.assertEqual(result['total_votes'], 0)
        self.assertFalse(result['is_closed'])
    
    def test_get_poll_detail(self):
        created = self.service.create_poll(self.user, 'Detail', ['X', 'Y'])
        detail = self.service.get_poll_detail(created['id'])
        self.assertEqual(detail['title'], 'Detail')
    
    def test_vote_success(self):
        created = self.service.create_poll(self.user, 'Vote', ['Opt1', 'Opt2'])
        option_id = created['options'][0]['id']
    
        # 配置 Mock：让 incr 返回 1，让 get_counts 返回包含该选项计数的字典
        self.mock_counter.incr.return_value = 1
        self.mock_counter.get_counts.return_value = {option_id: 1}
    
        # 第一次投票
        result = self.service.vote(self.other_user, created['id'], [option_id])
    
        # 检查调用
        self.mock_counter.incr.assert_called_with(created['id'], option_id)
        self.mock_sender.send_vote_update.assert_called()
    
        # 检查返回的计数（来自 Redis）
        self.assertEqual(result['options'][0]['count'], 1)
    
    def test_vote_duplicate_rejected(self):
        created = self.service.create_poll(self.user, 'Dup', ['P', 'Q'])
        option_id = created['options'][0]['id']
        self.service.vote(self.other_user, created['id'], [option_id])
        # 再次投票应抛出异常
        with self.assertRaises(PermissionDenied):
            self.service.vote(self.other_user, created['id'], [option_id])
    
    def test_vote_poll_closed(self):
        from django.utils import timezone
        import datetime
        created = self.service.create_poll(
            self.user, 'Closed', ['Yes', 'No'],
            closes_at=timezone.now() - datetime.timedelta(days=1)
        )
        option_id = created['options'][0]['id']
        with self.assertRaises(PermissionDenied):
            self.service.vote(self.other_user, created['id'], [option_id])
    
    def test_list_my_polls(self):
        self.service.create_poll(self.user, 'My1', ['a'])
        self.service.create_poll(self.user, 'My2', ['b'])
        self.service.create_poll(self.other_user, 'Other', ['c'])
        mine = self.service.list_my_polls(self.user)
        self.assertEqual(len(mine), 2)
# polls/tests/__init__.py 可以空着
# polls/tests/test_services.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from polls.services import PollService
from polls.repositories import PollRepository, VoteRepository
from unittest.mock import patch, MagicMock
from django.core.exceptions import PermissionDenied

User = get_user_model()

class PollServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.service = PollService()
        # 使用真实的 Repository（因为使用 SQLite，测试环境可以直接用内存数据库）
    
    def test_create_poll(self):
        result = self.service.create_poll(
            user=self.user,
            title='Favorite Color',
            options=['Red', 'Blue'],
            is_multiple=False
        )
        self.assertIn('id', result)
        self.assertEqual(result['title'], 'Favorite Color')
        self.assertEqual(len(result['options']), 2)
        self.assertEqual(result['total_votes'], 0)

    def test_vote_success(self):
        poll = self.service.create_poll(self.user, 'Test', ['A', 'B'])
        result = self.service.vote(self.user, poll['id'], [1])  # 选项1
        self.assertEqual(result['options'][0]['count'], 1)
        # 重复投票应抛异常
        with self.assertRaises(PermissionDenied):
            self.service.vote(self.user, poll['id'], [1])

    def test_vote_poll_closed(self):
        from django.utils import timezone
        import datetime
        poll = self.service.create_poll(
            self.user, 'Closed', ['Yes', 'No'],
            closes_at=timezone.now() - datetime.timedelta(days=1)
        )
        with self.assertRaises(PermissionDenied):
            self.service.vote(self.user, poll['id'], [1])
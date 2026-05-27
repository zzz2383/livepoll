# polls/tests/test_views.py
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock

User = get_user_model()

class PollAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='apitester', password='testpass')
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        
        # 启动 mock
        self.counter_patcher = patch('polls.services.RedisVoteCounter')
        self.sender_patcher = patch('polls.services.MessageSender')
        self.mock_counter_cls = self.counter_patcher.start()
        self.mock_sender_cls = self.sender_patcher.start()
        
        # 配置默认行为
        self.mock_counter = MagicMock()
        self.mock_counter.get_counts.return_value = {}
        self.mock_counter.incr.return_value = 1
        self.mock_counter_cls.return_value = self.mock_counter
        
        self.addCleanup(self.counter_patcher.stop)
        self.addCleanup(self.sender_patcher.stop)
    
    def test_create_poll_success(self):
        response = self.client.post('/api/polls/', {
            'title': 'API Poll',
            'options': ['One', 'Two'],
            'is_multiple': False
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'API Poll')
        self.assertEqual(len(response.data['options']), 2)
    
    def test_list_polls(self):
        self.client.post('/api/polls/', {
            'title': 'List1', 'options': ['a', 'b']
        }, format='json')
        response = self.client.get('/api/polls/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_vote_success(self):
        create_resp = self.client.post('/api/polls/', {
            'title': 'VoteAPI', 'options': ['X', 'Y']
        }, format='json')
        poll_id = create_resp.data['id']
        option_id = create_resp.data['options'][0]['id']
        
        # 配置 Mock 的 get_counts 返回值，使其在投票后返回计数 1
        self.mock_counter.get_counts.return_value = {option_id: 1}
    
        other_user = User.objects.create_user(username='other_api', password='pass')
        refresh = RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
        vote_resp = self.client.post(f'/api/polls/{poll_id}/vote/', {
            'option_ids': [option_id]
        }, format='json')
        self.assertEqual(vote_resp.status_code, 200)
        self.assertEqual(vote_resp.data['options'][0]['count'], 1)
    
    def test_duplicate_vote_rejected(self):
        create_resp = self.client.post('/api/polls/', {
            'title': 'DupAPI', 'options': ['A', 'B']
        }, format='json')
        poll_id = create_resp.data['id']
        option_id = create_resp.data['options'][0]['id']
        other_user = User.objects.create_user(username='other_dup', password='pass')
        refresh = RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
        self.client.post(f'/api/polls/{poll_id}/vote/', {'option_ids': [option_id]}, format='json')
        vote2 = self.client.post(f'/api/polls/{poll_id}/vote/', {'option_ids': [option_id]}, format='json')
        self.assertEqual(vote2.status_code, 403)
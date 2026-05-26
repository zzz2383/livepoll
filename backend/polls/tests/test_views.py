# polls/tests/test_views.py
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class PollAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='apitester', password='testpass')
        # 获取 JWT token
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_create_and_list_polls(self):
        # 创建投票
        response = self.client.post('/api/polls/', {
            'title': 'Poll 1',
            'options': ['Opt A', 'Opt B'],
            'is_multiple': False
        }, format='json')
        self.assertEqual(response.status_code, 201)
        poll_id = response.data['id']

        # 获取列表
        list_response = self.client.get('/api/polls/')
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 1)

    def test_vote_flow(self):
        # 创建
        create_res = self.client.post('/api/polls/', {
            'title': 'Vote Test',
            'options': ['X', 'Y']
        }, format='json')
        poll_id = create_res.data['id']
        # 投票
        vote_res = self.client.post(f'/api/polls/{poll_id}/vote/', {
            'option_ids': [create_res.data['options'][0]['id']]
        }, format='json')
        self.assertEqual(vote_res.status_code, 200)
        # 检查票数
        detail_res = self.client.get(f'/api/polls/{poll_id}/')
        self.assertEqual(detail_res.data['options'][0]['count'], 1)
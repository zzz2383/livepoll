# users/tests/test_services.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from users.services import UserService
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserServiceTest(TestCase):
    def setUp(self):
        self.service = UserService()

    def test_register(self):
        result = self.service.register('newuser', 'new@example.com', 'strongpass')
        self.assertIn('user', result)
        self.assertIn('access', result)
        self.assertIn('refresh', result)
        self.assertEqual(result['user']['username'], 'newuser')
        # 验证用户确实在数据库中
        user = User.objects.get(username='newuser')
        self.assertIsNotNone(user)

    def test_register_missing_fields(self):
        with self.assertRaises(ValueError):
            self.service.register('', '', '')

    def test_login_success(self):
        User.objects.create_user(username='loginuser', password='testpass')
        result = self.service.login('loginuser', 'testpass')
        self.assertIn('access', result)
        self.assertEqual(result['user']['username'], 'loginuser')

    def test_login_invalid_credentials(self):
        User.objects.create_user(username='loginuser', password='testpass')
        with self.assertRaises(ValueError):
            self.service.login('loginuser', 'wrongpass')

    def test_refresh_token_success(self):
        user = User.objects.create_user(username='refreshuser', password='testpass')
        refresh = RefreshToken.for_user(user)
        old_refresh_str = str(refresh)
        result = self.service.refresh_token(old_refresh_str)
        self.assertIn('access', result)
        self.assertIn('refresh', result)
        # 旧的 refresh 应该失效（旋转令牌开启 BLACKLIST 后需要验证，这里仅检查能返回新令牌即可）
        # 如果未启用 blacklist app，旧令牌仍可用，但不影响测试

    def test_refresh_token_invalid(self):
        with self.assertRaises(ValueError):
            self.service.refresh_token('invalidtoken')
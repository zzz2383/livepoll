# users/services.py
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from users.repositories import UserRepository

class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    def register(self, username: str, email: str, password: str) -> dict:
        """
        注册新用户，返回用户信息和 token
        """
        if not username or not password:
            raise ValueError("Username and password are required")
        user = self.user_repo.create_user(username, email, password)
        refresh = RefreshToken.for_user(user)
        return {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

    def login(self, username: str, password: str) -> dict:
        """
        验证用户并返回 token
        """
        user = authenticate(username=username, password=password)
        if not user:
            raise ValueError("Invalid credentials")
        refresh = RefreshToken.for_user(user)
        return {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

    def refresh_token(self, refresh_token_str: str) -> dict:
        """
        刷新 access token
        """
        try:
            refresh = RefreshToken(refresh_token_str)
            # 旋转刷新令牌（生成新的 refresh 和 access）
            new_access = str(refresh.access_token)
            refresh.set_jti()  # 旧 token 加入黑名单（如果启用 blacklist app）
            refresh.set_exp()
            new_refresh = str(refresh)
            return {
                'access': new_access,
                'refresh': new_refresh,
            }
        except Exception:
            raise ValueError("Invalid or expired refresh token")
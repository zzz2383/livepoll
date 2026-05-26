# users/repositories.py
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class UserRepository:
    """封装 User 模型的数据访问，不包含业务逻辑"""

    def create_user(self, username: str, email: str, password: str) -> User: # pyright: ignore[reportInvalidTypeForm]
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            return user
        except IntegrityError:
            raise ValueError("Username or email already exists")

    def get_user_by_username(self, username: str) -> User | None: # pyright: ignore[reportInvalidTypeForm]
        return User.objects.filter(username=username).first()

    def get_user_by_id(self, user_id: int) -> User | None: # pyright: ignore[reportInvalidTypeForm]
        return User.objects.filter(id=user_id).first()
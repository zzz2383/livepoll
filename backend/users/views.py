# users/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from users.services import UserService
from users.serializers import (
    RegisterSerializer, LoginSerializer, TokenRefreshSerializer, UserSerializer
)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            service = UserService()
            result = service.register(
                username=serializer.validated_data['username'],
                email=serializer.validated_data.get('email', ''),
                password=serializer.validated_data['password']
            )
            # 序列化响应
            return Response({
                'user': UserSerializer(result['user']).data,
                'access': result['access'],
                'refresh': result['refresh'],
            }, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            service = UserService()
            result = service.login(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            return Response({
                'user': UserSerializer(result['user']).data,
                'access': result['access'],
                'refresh': result['refresh'],
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    serializer_class = TokenRefreshSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            service = UserService()
            result = service.refresh_token(serializer.validated_data['refresh'])
            return Response(result)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
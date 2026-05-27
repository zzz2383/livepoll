# polls/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .services import PollService
from .serializers import PollCreateSerializer, VoteSerializer

class PollListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取当前用户创建的投票列表"""
        service = PollService()
        polls = service.list_my_polls(request.user)
        return Response(polls)

    def post(self, request):
        """创建新投票"""
        serializer = PollCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = PollService()
        data = serializer.validated_data
        poll_dict = service.create_poll(
            user=request.user,
            title=data['title'],
            options=data['options'],
            is_multiple=data.get('is_multiple', False),
            closes_at=data.get('closes_at')
        )
        return Response(poll_dict, status=status.HTTP_201_CREATED)

class PollDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, poll_id):
        service = PollService()
        poll = service.get_poll_detail(poll_id)
        return Response(poll)

class PollVoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, poll_id):
        serializer = VoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = PollService()
        try:
            updated_poll = service.vote(
                user=request.user,
                poll_id=poll_id,
                option_ids=serializer.validated_data['option_ids']
            )
            return Response(updated_poll)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class ParticipatedPollsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = PollService()
        polls = service.list_participated_polls(request.user)
        return Response(polls)
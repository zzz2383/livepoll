# polls/urls.py
from django.urls import path
from .views import PollListCreateView, PollDetailView, PollVoteView, ParticipatedPollsView

urlpatterns = [
    path('', PollListCreateView.as_view(), name='poll_list_create'),
    path('participated/', ParticipatedPollsView.as_view(), name='poll_participated'),
    path('<int:poll_id>/', PollDetailView.as_view(), name='poll_detail'),
    path('<int:poll_id>/vote/', PollVoteView.as_view(), name='poll_vote'),
]
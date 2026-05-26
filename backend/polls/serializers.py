# polls/serializers.py
from rest_framework import serializers

class PollCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    options = serializers.ListField(
        child=serializers.CharField(max_length=200),
        min_length=2,
        help_text="At least 2 options required"
    )
    is_multiple = serializers.BooleanField(default=False)
    closes_at = serializers.DateTimeField(required=False, allow_null=True)

class VoteSerializer(serializers.Serializer):
    option_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
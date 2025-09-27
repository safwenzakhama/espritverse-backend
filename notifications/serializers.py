from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "display_name", "avatar_url", "role")

class NotificationSerializer(serializers.ModelSerializer):
    actor = ActorSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "type",
            "actor",
            "post",
            "comment",
            "friend_request",
            "is_read",
            "created_at",
        )
        read_only_fields = fields

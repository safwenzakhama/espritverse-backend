from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'display_name', 'avatar_url', 'role')


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender', 'content', 'image', 'image_url', 'is_read', 'created_at')
        read_only_fields = ('sender', 'created_at', 'image_url')

    def validate(self, data):
        """Validate that either content or image is provided"""
        content = data.get('content', '')
        image = data.get('image')
        
        # Allow empty content if image is provided
        if not content and not image:
            raise serializers.ValidationError("Either content or image must be provided")
        
        return data

    def get_image_url(self, obj):
        return obj.image_url


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'participants', 'last_message', 'unread_count', 'other_participant', 'created_at', 'updated_at')
        read_only_fields = ('participants', 'created_at', 'updated_at')

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0

    def get_other_participant(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            other = obj.participants.exclude(id=request.user.id).first()
            if other:
                return UserSerializer(other).data
        return None


class CreateConversationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
            if user == self.context['request'].user:
                raise serializers.ValidationError("Cannot create conversation with yourself")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

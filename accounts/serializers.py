from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FriendRequest  # make sure FriendRequest is defined in models.py
from .models import Role

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ("username", "email", "password", "display_name", "role", "avatar")
        extra_kwargs = {
            'avatar': {'required': False, 'allow_null': True},
            'role': {'required': False}  # Role is optional, defaults to student
        }
    
    def validate_role(self, value):
        # Only allow student role for self-registration
        if value and value != Role.STUDENT:
            raise serializers.ValidationError("Only student role is allowed for self-registration. Contact admin for other roles.")
        return value or Role.STUDENT  # Default to student if not provided
    
    def create(self, validated_data):
        pwd = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(pwd)
        user.save()
        return user

class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","username","email","display_name","bio","avatar_url","role")

class UpdateMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("display_name","bio","avatar_url")

# what others see (public profile)
class PublicProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "display_name", "bio", "role", "avatar_url")

    def get_avatar_url(self, obj):
        # works with ImageField property from model
        try:
            return obj.avatar.url if obj.avatar else None
        except Exception:
            return None

# what the owner can edit
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("display_name", "bio", "avatar")  # avatar accepts multipart file

class UserPublicSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "display_name", "role", "avatar_url")

    def get_avatar_url(self, obj):
        try:
            return obj.avatar.url if obj.avatar else None
        except Exception:
            return None


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = UserPublicSerializer(read_only=True)
    receiver = UserPublicSerializer(read_only=True)
    # allow sending request by passing receiver_id
    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="receiver",
        write_only=True
    )

    class Meta:
        model = FriendRequest
        fields = ("id", "sender", "receiver", "receiver_id", "status", "created_at")
        read_only_fields = ("status", "created_at")

    def validate(self, attrs):
        sender = self.context["request"].user
        receiver = attrs["receiver"]
        
        print(f"FriendRequest validation - Sender: {sender.id} ({sender.username}), Receiver: {receiver.id} ({receiver.username})")
        
        if sender == receiver:
            raise serializers.ValidationError("You cannot send a friend request to yourself.")
        
        # Check if there's already a pending friend request
        pending_requests = FriendRequest.objects.filter(sender=sender, receiver=receiver, status=FriendRequest.PENDING)
        print(f"Pending requests found: {list(pending_requests.values_list('id', 'status'))}")
        
        if pending_requests.exists():
            raise serializers.ValidationError("Friend request already sent.")
        
        # Check if they're already friends
        existing_friends = FriendRequest.objects.filter(
            sender__in=[sender, receiver], 
            receiver__in=[sender, receiver], 
            status=FriendRequest.ACCEPTED
        )
        print(f"Existing friends found: {list(existing_friends.values_list('id', 'sender__username', 'receiver__username', 'status'))}")
        
        if existing_friends.exists():
            raise serializers.ValidationError("You are already friends with this user.")
        
        return attrs

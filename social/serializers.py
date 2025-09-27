from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, PostLike, CommentLike, Section

User = get_user_model()

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "display_name", "avatar_url", "role")

class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    is_liked = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id", "post", "author", "content",
            "image", "image_url",
            "created_at", "updated_at", "likes_count", "is_liked",
        )
        read_only_fields = ("author", "created_at", "updated_at", "likes_count", "image_url", "is_liked")

    def get_image_url(self, obj):
        try:
            return obj.image.url if obj.image else None
        except Exception:
            return None

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    is_liked = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id", "section", "target_user",
            "author", "title", "content",
            "image", "image_url",
            "created_at", "updated_at",
            "is_pinned", "comments_count", "likes_count", "is_liked",
        )
        read_only_fields = ("author", "created_at", "updated_at", "comments_count", "likes_count", "image_url", "is_liked")

    def get_image_url(self, obj):
        try:
            return obj.image.url if obj.image else None
        except Exception:
            return None

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def validate(self, attrs):
        section = attrs.get("section", getattr(self.instance, "section", None))
        target_user = attrs.get("target_user", getattr(self.instance, "target_user", None))
        if section == Section.PROFILE and not target_user:
            raise serializers.ValidationError("PROFILE posts require target_user.")
        if section != Section.PROFILE and target_user:
            raise serializers.ValidationError("target_user is only allowed for PROFILE posts.")
        return attrs

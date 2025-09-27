# social/views.py

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from .models import Post, Comment, PostLike, CommentLike, Section
from accounts.models import FriendRequest
from accounts.serializers import UserPublicSerializer
from .serializers import PostSerializer, CommentSerializer
from .permissions import CanCreatePost, IsAuthorOrAdminOrReadOnly, CanCreateComment
from .utils import get_friend_ids
from .content_moderation import ContentModerationService
from notifications.models import Notification, NotificationType
from django.db.models import Q, Case, When, Value, IntegerField
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    """
    Posts across sections:
      - section filters: ?section=lost_and_found | colocation | club | esprit_committee | profile
      - author filter:   ?username=<author_username>
      - profile walls:   ?target_user=<user_id> (only with section=profile)
    Create rules enforced by CanCreatePost (roles).
    """
    queryset = (
        Post.objects.select_related("author", "target_user")
        .all()
        .order_by("-created_at")
    )
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated & CanCreatePost & IsAuthorOrAdminOrReadOnly]
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_queryset(self):
        qs = super().get_queryset()
        section = self.request.query_params.get("section")
        username = self.request.query_params.get("username")
        target_user = self.request.query_params.get("target_user")

        if section:
            qs = qs.filter(section=section)
        if username:
            qs = qs.filter(author__username=username)
        if target_user:
            qs = qs.filter(section=Section.PROFILE, target_user_id=target_user)
        return qs

    def create(self, request, *args, **kwargs):
        """Override create method to handle content moderation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get the post data before saving
        post_data = serializer.validated_data
        title = post_data.get('title', '')
        content = post_data.get('content', '')
        section = post_data.get('section', '')
        
        # Initialize content moderation service
        try:
            moderation_service = ContentModerationService()
            is_approved, reason = moderation_service.moderate_content(title, content, section)
            
            if not is_approved:
                # Create notification for the user about rejection
                Notification.objects.create(
                    recipient=request.user,
                    type=NotificationType.POST_REJECTED,
                    post=None,  # No post created yet
                )
                
                # Notify admins about the rejected post
                admin_users = User.objects.filter(is_staff=True)
                for admin in admin_users:
                    Notification.objects.create(
                        recipient=admin,
                        actor=request.user,
                        type=NotificationType.MODERATION_ALERT,
                        post=None,
                    )
                
                # Return custom error response with moderation feedback
                feedback = moderation_service.get_moderation_feedback(title, content, section, reason)
                error_data = {
                    'non_field_errors': [f"Post rejected: {reason}"],
                    'moderation_feedback': feedback
                }
                logger.info(f"Returning moderation rejection: {error_data}")
                
                from rest_framework.response import Response
                from rest_framework import status
                return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Content moderation error: {str(e)}")
            # If moderation fails, be conservative and reject
            from rest_framework.response import Response
            from rest_framework import status
            return Response({
                'non_field_errors': ["Content moderation system temporarily unavailable. Please try again later."]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # If approved, save the post and return success response
        serializer.save(author=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # --- Likes on posts ---
    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        PostLike.objects.get_or_create(post=post, user=request.user)
        return Response({"liked": True, "likes_count": post.likes.count()})

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        PostLike.objects.filter(post=post, user=request.user).delete()
        return Response({"liked": False, "likes_count": post.likes.count()})

    # --- Nested comments on a post ---
    @action(
        detail=True,
        methods=["GET", "POST"],
        permission_classes=[IsAuthenticated, CanCreateComment],
        parser_classes=[JSONParser, FormParser, MultiPartParser],
    )
    def comments(self, request, pk=None):
        post = self.get_object()

        if request.method == "GET":
            qs = post.comments.select_related("author").all().order_by("created_at")
            page = self.paginate_queryset(qs)
            if page is not None:
                ser = CommentSerializer(page, many=True, context={"request": request})
                return self.get_paginated_response(ser.data)
            ser = CommentSerializer(qs, many=True, context={"request": request})
            return Response(ser.data)

        # POST: create a comment (supports text and optional image)
        ser = CommentSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        ser.save(post=post, author=request.user)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Top-level CRUD for comments (useful for edit/delete/like via /api/comments/{id}/).
    To create under a post, you can use:
      - POST /api/posts/{post_id}/comments/   (nested action), OR
      - POST /api/comments/  with body { "post": <post_id>, ... }
    """
    queryset = (
        Comment.objects.select_related("author", "post")
        .all()
        .order_by("created_at")
    )
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrAdminOrReadOnly]
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # --- Likes on comments ---
    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        CommentLike.objects.get_or_create(comment=comment, user=request.user)
        return Response({"liked": True, "likes_count": comment.likes.count()})

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        comment = self.get_object()
        CommentLike.objects.filter(comment=comment, user=request.user).delete()
        return Response({"liked": False, "likes_count": comment.likes.count()})

# ---------------------------- FEED START
class _SectionFeedBase(generics.ListAPIView):
    """
    Base class for section-specific feeds.
    Supports:
      - ?q=keyword     (title/content)
      - ?username=foo  (author username)
      - ?only_friends=true|false  (default: false) -> restrict to my friends + me
      - ?friends_first=true|false (default: true)  -> bubble friends to top
      - ?date_from=YYYY-MM-DD, ?date_to=YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    section = None  # override in subclasses; None means don't filter by section

    def get_queryset(self):
        user = self.request.user
        qs = Post.objects.select_related("author", "target_user").all()

        # section filter (skip for profile; handled in subclass)
        if self.section is not None:
            qs = qs.filter(section=self.section)

        # friends options
        only_friends = self.request.query_params.get("only_friends", "false").lower() in {"1","true","yes"}
        friends_first = self.request.query_params.get("friends_first", "true").lower() in {"1","true","yes"}

        friend_ids = set()
        if only_friends or friends_first:
            friend_ids = get_friend_ids(user.id)

        if only_friends:
            qs = qs.filter(author_id__in=friend_ids | {user.id})

        # keyword
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))

        # author username
        username = self.request.query_params.get("username")
        if username:
            qs = qs.filter(author__username__iexact=username)

        # date range
        from django.utils.dateparse import parse_date
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(created_at__date__gte=parse_date(date_from))
        if date_to:
            qs = qs.filter(created_at__date__lte=parse_date(date_to))

        # ordering: pinned first, then friends (if enabled), then newest
        if friends_first and friend_ids:
            qs = qs.annotate(
                is_friend=Case(
                    When(author_id__in=friend_ids | {user.id}, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by("is_friend", "-is_pinned", "-created_at")
        else:
            qs = qs.order_by("-is_pinned", "-created_at")

        return qs


class CommitteeFeedView(_SectionFeedBase):
    """Only committee section posts (anyone can view)."""
    section = Section.ESPRIT_COMMITTEE


class ClubFeedView(_SectionFeedBase):
    """Only club section posts (anyone can view)."""
    section = Section.CLUB


class LostFoundFeedView(_SectionFeedBase):
    """Only lost & found posts (anyone can view)."""
    section = Section.LOST_AND_FOUND


class ColocationFeedView(_SectionFeedBase):
    """Only colocation posts (anyone can view)."""
    section = Section.COLOCATION


class ProfileFeedView(_SectionFeedBase):
    """
    Profile wall feed.
    Use either:
      - /api/feed/profile/<int:user_id>/
      - or /api/feed/profile/?target_user=<id>
    """
    section = None  # we'll filter explicitly

    def get_queryset(self):
        qs = super().get_queryset()
        # enforce profile section + target user
        target_id = self.kwargs.get("user_id") or self.request.query_params.get("target_user")
        if not target_id:
            # return empty if not specified; or raise ValidationError
            return Post.objects.none()
        return qs.filter(section=Section.PROFILE, target_user_id=target_id)

# ---------------------------- FEED END

class FriendsListView(generics.ListAPIView):
    """
    GET /api/friends/  -> list of my friends (users)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserPublicSerializer

    def get_queryset(self):
        ids = get_friend_ids(self.request.user.id)
        return User.objects.filter(id__in=ids).order_by("username")


class UnfriendView(APIView):
    """
    POST /api/friends/unfriend/  body: {"user_id": <int>}
    Deletes any ACCEPTED link between the two users.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        other_id = request.data.get("user_id")
        if not other_id:
            return Response({"detail": "user_id is required"}, status=400)
        me = request.user
        deleted, _ = FriendRequest.objects.filter(
            status=FriendRequest.ACCEPTED,
            sender_id__in=[me.id, other_id],
            receiver_id__in=[me.id, other_id],
        ).delete()
        return Response({"unfriended": bool(deleted)}, status=status.HTTP_200_OK)

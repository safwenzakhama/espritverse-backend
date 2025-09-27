# accounts/views.py

from django.contrib.auth import get_user_model
from django.db import models

from rest_framework import generics, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import FriendRequest
from .permissions import IsSelfOrReadOnly
from .serializers import (
    RegisterSerializer,
    UserMeSerializer,
    UserPublicSerializer,
    UpdateMeSerializer,
    FriendRequestSerializer,
    PublicProfileSerializer,
    ProfileUpdateSerializer,
)

User = get_user_model()


# --- Auth ---
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def get_serializer_class(self):
        return RegisterSerializer


class LoginView(TokenObtainPairView):  # returns access+refresh
    permission_classes = [AllowAny]


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


# --- Users ---
class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserMeSerializer
    permission_classes = [IsAuthenticated, IsSelfOrReadOnly]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UpdateMeSerializer
        return UserMeSerializer


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all().order_by("id")
    permission_classes = [IsAuthenticated]
    serializer_class = UserPublicSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        
        # First exclude users that should never appear in search results
        current_user = self.request.user
        qs = qs.exclude(id=current_user.id)  # Exclude current user
        qs = qs.exclude(role='admin')  # Exclude admin users
        qs = qs.exclude(username__iexact='admin')  # Exclude user with username 'admin'
        qs = qs.exclude(username__iexact='authorized user')  # Exclude 'authorized user'
        qs = qs.exclude(username__icontains='admin')  # Exclude any username containing 'admin'
        
        # Then apply search filter
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(username__icontains=q)
        
        return qs


# --- Friend Requests ---
class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.select_related("sender", "receiver").order_by("-created_at")
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        box = self.request.query_params.get("box", "inbox")  # inbox|outbox|all
        qs = super().get_queryset()
        if box == "inbox":
            return qs.filter(receiver=user)
        elif box == "outbox":
            return qs.filter(sender=user)
        # union of inbox + outbox for current user
        return (qs.filter(receiver=user) | qs.filter(sender=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=["POST"])
    def accept(self, request, pk=None):
        fr = self.get_object()
        if fr.receiver != request.user:
            return Response({"detail": "Not allowed."}, status=403)
        fr.status = FriendRequest.ACCEPTED
        fr.save(update_fields=["status"])
        return Response(self.get_serializer(fr).data)

    @action(detail=True, methods=["POST"])
    def decline(self, request, pk=None):
        fr = self.get_object()
        if fr.receiver != request.user:
            return Response({"detail": "Not allowed."}, status=403)
        # Delete the friend request instead of just marking as declined
        fr.delete()
        return Response({"detail": "Friend request declined and removed."})

    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk=None):
        # For cancel action, we need to check both sent and received requests
        # Override the queryset to include all requests for the current user
        user = request.user
        qs = FriendRequest.objects.select_related("sender", "receiver").filter(
            models.Q(sender=user) | models.Q(receiver=user)
        )
        
        try:
            fr = qs.get(pk=pk)
        except FriendRequest.DoesNotExist:
            return Response({"detail": "Friend request not found."}, status=404)
            
        if fr.sender != request.user:
            return Response({"detail": "Not allowed."}, status=403)
        fr.delete()
        return Response({"detail": "Friend request cancelled."})


# --- Profiles ---
class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/profiles/               -> list (search ?q=)
    /api/profiles/{username}/    -> retrieve public profile by username or email
    /api/profiles/me/            -> GET my profile
    /api/profiles/me/            -> PATCH { display_name, bio, avatar }
    """
    queryset = User.objects.all().order_by("id")
    permission_classes = [IsAuthenticated]
    serializer_class = PublicProfileSerializer
    lookup_field = "username"  # enable /profiles/{username}/

    def get_object(self):
        lookup_value = self.kwargs[self.lookup_field]
        # Try to find by username first, then by email
        try:
            return User.objects.get(username=lookup_value)
        except User.DoesNotExist:
            try:
                return User.objects.get(email=lookup_value)
            except User.DoesNotExist:
                from django.http import Http404
                raise Http404("Profile not found")

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(username__icontains=q)
        return qs

    @action(detail=False, methods=["GET", "PATCH"], url_path="me")
    def me(self, request):
        user = request.user
        if request.method == "GET":
            return Response(PublicProfileSerializer(user, context={"request": request}).data)
        # PATCH (multipart supported for avatar)
        serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(PublicProfileSerializer(user, context={"request": request}).data)

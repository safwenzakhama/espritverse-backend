# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, RefreshView,
    MeView, UserViewSet, FriendRequestViewSet, ProfileViewSet
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"friends/requests", FriendRequestViewSet, basename="friend-requests")
router.register(r"profiles", ProfileViewSet, basename="profiles")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/",    LoginView.as_view(),    name="login"),
    path("auth/refresh/",  RefreshView.as_view(),  name="refresh"),
    path("users/me/",      MeView.as_view(),       name="me"),
    path("", include(router.urls)),
]

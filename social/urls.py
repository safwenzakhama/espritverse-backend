# social/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet, CommentViewSet,
    CommitteeFeedView, ClubFeedView, LostFoundFeedView, ColocationFeedView, ProfileFeedView, FriendsListView, UnfriendView
)

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="posts")
router.register(r"comments", CommentViewSet, basename="comments")

urlpatterns = [
    # Section-specific feeds
    path("feed/committee/", CommitteeFeedView.as_view(), name="feed-committee"),
    path("feed/club/",      ClubFeedView.as_view(),      name="feed-club"),
    path("feed/lost-found/", LostFoundFeedView.as_view(), name="feed-lost-found"),
    path("feed/colocation/", ColocationFeedView.as_view(), name="feed-colocation"),
    path("feed/profile/<int:user_id>/", ProfileFeedView.as_view(), name="feed-profile-by-id"),
    path("feed/profile/",ProfileFeedView.as_view(), name="feed-profile"),


    path("friends/", FriendsListView.as_view(), name="friends-list"),
    path("friends/unfriend/", UnfriendView.as_view(), name="friends-unfriend"),
    path("", include(router.urls)),
]

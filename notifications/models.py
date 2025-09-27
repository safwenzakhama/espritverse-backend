from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class NotificationType(models.TextChoices):
    COMMENT_ON_POST = "comment_on_post", "Comment on your post"
    LIKE_ON_POST    = "like_on_post", "Like on your post"
    LIKE_ON_COMMENT = "like_on_comment", "Like on your comment"
    FRIEND_REQUEST  = "friend_request", "New friend request"
    FRIEND_ACCEPTED = "friend_accepted", "Friend request accepted"
    NEW_MESSAGE     = "new_message", "New message"
    POST_REJECTED   = "post_rejected", "Post rejected by content moderation"
    MODERATION_ALERT = "moderation_alert", "Content moderation alert for admins"

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications_caused")

    type = models.CharField(max_length=32, choices=NotificationType.choices)

    # Optional context
    post = models.ForeignKey("social.Post", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    comment = models.ForeignKey("social.Comment", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    friend_request = models.ForeignKey("accounts.FriendRequest", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} → {self.recipient} (by {self.actor})"

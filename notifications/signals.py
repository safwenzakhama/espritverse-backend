from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification, NotificationType
from social.models import Comment, PostLike, CommentLike
from accounts.models import FriendRequest

# --- Comment created -> notify post author (not self) ---
@receiver(post_save, sender=Comment)
def notify_comment_on_post(sender, instance: Comment, created, **kwargs):
    if not created:
        return
    post = instance.post
    actor = instance.author
    recipient = post.author
    if actor_id := getattr(actor, "id", None):
        if recipient and recipient.id != actor_id:
            Notification.objects.create(
                recipient=recipient,
                actor=actor,
                type=NotificationType.COMMENT_ON_POST,
                post=post,
                comment=instance,
            )

# --- Post liked -> notify post author (not self) ---
@receiver(post_save, sender=PostLike)
def notify_like_on_post(sender, instance: PostLike, created, **kwargs):
    if not created:
        return
    post = instance.post
    actor = instance.user
    recipient = post.author
    if recipient and recipient.id != actor.id:
        Notification.objects.create(
            recipient=recipient,
            actor=actor,
            type=NotificationType.LIKE_ON_POST,
            post=post,
        )

# --- Comment liked -> notify comment author (not self) ---
@receiver(post_save, sender=CommentLike)
def notify_like_on_comment(sender, instance: CommentLike, created, **kwargs):
    if not created:
        return
    comment = instance.comment
    actor = instance.user
    recipient = comment.author
    if recipient and recipient.id != actor.id:
        Notification.objects.create(
            recipient=recipient,
            actor=actor,
            type=NotificationType.LIKE_ON_COMMENT,
            comment=comment,
            post=comment.post,
        )

# --- Friend request created -> notify receiver ---
@receiver(post_save, sender=FriendRequest)
def notify_friend_request(sender, instance: FriendRequest, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.receiver,
            actor=instance.sender,
            type=NotificationType.FRIEND_REQUEST,
            friend_request=instance,
        )
        return

    # status changed to accepted -> notify sender
    if instance.status == FriendRequest.ACCEPTED:
        Notification.objects.get_or_create(
            recipient=instance.sender,
            actor=instance.receiver,
            type=NotificationType.FRIEND_ACCEPTED,
            friend_request=instance,
        )

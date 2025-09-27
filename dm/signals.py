from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message
from notifications.models import Notification

User = get_user_model()


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """Create a notification when a new message is sent"""
    if created:
        # Get the other participant in the conversation
        conversation = instance.conversation
        sender = instance.sender
        
        # Find the receiver (other participant)
        receiver = conversation.participants.exclude(id=sender.id).first()
        
        if receiver:
            # Create notification for the receiver
            Notification.objects.create(
                recipient=receiver,
                actor=sender,
                type='new_message',
                is_read=False
            )

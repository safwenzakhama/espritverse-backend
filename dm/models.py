from django.db import models
from django.conf import settings
from django.utils import timezone
from cloudinary.models import CloudinaryField

User = settings.AUTH_USER_MODEL


class Conversation(models.Model):
    """A conversation between two users"""
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        participants = list(self.participants.all())
        if len(participants) == 2:
            return f"Conversation between {participants[0].username} and {participants[1].username}"
        return f"Conversation with {len(participants)} participants"

    @property
    def other_participant(self, user):
        """Get the other participant in a 1-on-1 conversation"""
        return self.participants.exclude(id=user.id).first()


class Message(models.Model):
    """A message in a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    image = CloudinaryField("image", folder="espritverse/messages", blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} in conversation {self.conversation.id}"

    @property
    def image_url(self):
        return self.image.url if self.image else None

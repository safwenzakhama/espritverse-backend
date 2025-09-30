# accounts models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    COMMITTEE_ADMIN = "committee_admin", "Committee Admin"
    STUDENT = "student", "Student"
    CLUB_MANAGER = "club_manager", "Club Manager"

class User(AbstractUser):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    # avatar file (served from /media/avatars/ in dev)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.STUDENT)

    REQUIRED_FIELDS = ["email"]

    @property
    def avatar_url(self):
        return self.avatar.url if self.avatar else None

class FriendRequest(models.Model):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    STATUS_CHOICES = [(PENDING,"Pending"), (ACCEPTED,"Accepted"), (DECLINED,"Declined")]

    sender = models.ForeignKey(User, related_name="sent_requests", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_requests", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Remove unique constraint to allow resending friend requests
        pass

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.status})"

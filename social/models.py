from django.conf import settings
from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField

User = settings.AUTH_USER_MODEL

class Section(models.TextChoices):
    ESPRIT_COMMITTEE = "esprit_committee", "ESPRIT Committee"
    CLUB = "club", "Club"
    LOST_AND_FOUND = "lost_and_found", "Lost And Found"
    COLOCATION = "colocation", "Colocation"
    PROFILE = "profile", "Profile"

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    section = models.CharField(max_length=32, choices=Section.choices)
    target_user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE, related_name="wall_posts"
    )
    title = models.CharField(max_length=180, blank=True)
    content = models.TextField()
    # ✅ single image as attribute (stored on Cloudinary)
    image = CloudinaryField("image", folder="espritverse/posts", null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
            ordering = ["-created_at"]
            indexes = [
                models.Index(fields=["-created_at"]),
                models.Index(fields=["section"]),
            ]


    def __str__(self):
        return f"{self.section} | {self.author} | {self.title or self.content[:30]}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(blank=True)  # allow image-only comments if you like
    # ✅ single image as attribute (stored on Cloudinary)
    image = CloudinaryField("image", folder="espritverse/comments", null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_likes")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("post", "user")

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_likes")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("comment", "user")

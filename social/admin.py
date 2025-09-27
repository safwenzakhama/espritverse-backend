from django.contrib import admin
from .models import Post, Comment, PostLike, CommentLike

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "section", "author", "created_at", "is_pinned")
    list_filter = ("section", "is_pinned")

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created_at")

admin.site.register(PostLike)
admin.site.register(CommentLike)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, FriendRequest

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("Profile", {"fields": ("display_name","bio","avatar","role")}),)
    list_display = ("username","email","role","is_staff")

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("sender__username", "receiver__username", "sender__email", "receiver__email")
    readonly_fields = ("id", "created_at")
    ordering = ("-created_at",)

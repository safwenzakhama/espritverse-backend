# social/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS
from accounts.models import Role
from .models import Section


class CanCreatePost(BasePermission):
    """
    Controls who can CREATE posts per section.

    Rules:
    - ESPRIT_COMMITTEE: only COMMITTEE_ADMIN or ADMIN
    - CLUB: only CLUB_MANAGER or ADMIN
    - LOST_AND_FOUND, COLOCATION: any authenticated user
    - PROFILE: only the profile owner (target_user == request.user)
    - READ (GET/HEAD/OPTIONS): always allowed (handled elsewhere if you lock down)
    - UPDATE/DELETE are handled by IsAuthorOrAdminOrReadOnly
    """

    def has_permission(self, request, view):
        # allow safe reads
        if request.method in SAFE_METHODS:
            return True

        # only enforce for create on posts
        if getattr(view, "action", None) != "create":
            return True

        data = request.data
        section = data.get("section")
        if not section:
            return False  # must specify section when creating

        user = request.user
        user_role = getattr(user, "role", None)

        if section == Section.ESPRIT_COMMITTEE:
            return user_role in {Role.COMMITTEE_ADMIN, Role.ADMIN}

        if section == Section.CLUB:
            return user_role in {Role.CLUB_MANAGER, Role.ADMIN}

        if section in (Section.LOST_AND_FOUND, Section.COLOCATION):
            return user.is_authenticated

        if section == Section.PROFILE:
            target_user_id = data.get("target_user")
            # Only owner can post on their own profile wall
            return str(target_user_id) == str(user.id)

        return False


class IsAuthorOrAdminOrReadOnly(BasePermission):
    """
    For UPDATE/PATCH/DELETE on Post/Comment:
    - author can modify/delete their own
    - ADMIN can modify/delete anything
    - everyone can read (SAFE_METHODS)
    """

    def has_permission(self, request, view):
        # Allow all authenticated users to access the view
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        is_admin = getattr(user, "role", None) == Role.ADMIN
        author = getattr(obj, "author", None)
        return is_admin or (author == user)


class CanCreateComment(BasePermission):
    """
    Any authenticated user may create comments.
    Reads are allowed via SAFE_METHODS.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

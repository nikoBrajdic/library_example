from rest_framework.permissions import BasePermission


class IsApprovedAuthor(BasePermission):
    """Allow only authenticated users with an approved AuthorProfile."""

    message = "Only approved authors may perform this action."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        profile = getattr(user, "author_profile", None)
        return bool(profile and profile.is_approved)

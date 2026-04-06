"""
Role-based permissions classes used across the project.

Roles ( stored on User.role):
    VIEWER - read-only access to records & dashboard
    ANALYST - read records + dashboard summaries
    ADMIN - full CRUD on record and user

"""
from rest_framework.permissions import BasePermission
from apps.users.models import User, Role


class IsAdmin(BasePermission):
    """Only admin user are allowed."""
    message = "You must be an Admin to perform this action"

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role ==Role.ADMIN
        )


class IsAnalystOrAbove(BasePermission):
    """Analyst and admin users are allowed"""
    Message = "You must be an Analyst or admin to perform this action"

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (Role.ANALYST, Role.ADMIN)
        )


class IsActiveUser(BasePermission):
    """Blocks inactive (deactivated) accounts from any access."""
    message = "Your account is inactive. Contact an administrator."


    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active)


class ReadOnly(BasePermission):
    """Allows only safe HTTP methods (GET, HEAD, OPTIONS)."""

    def has_permission(self, request, view):
        return request.method in ("GET", "HEAD", "OPTIONS")

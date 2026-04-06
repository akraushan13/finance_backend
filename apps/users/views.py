from django.shortcuts import render

from ..core.permissions import IsActiveUser, IsAdmin

# Create your views here.

"""
User Management views
"""

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    AdminUserListSerializer,
    AdminUserCreateSerialzer,
    AdminUserUpdateSerializer
    )
from .models import User



from apps.users.token_blacklist import BlacklistedToken
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError


# Auth-adjacent
class RegisterView(generics.CreateAPIView):

    """
    POST /api/auth/register/
    Open endpoint - Creates a new VIEWER account.
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "Account created successfully.", "user": UserProfileSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )

class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Body: { "refresh": "<refresh token>" }
    Blacklists the token so it cannot be used again.
    """

    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": True, "message": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = UntypedToken(refresh_token)
            BlacklistedToken.objects.get_or_create(
                jti=token["jti"],
                defaults={"token": refresh_token},
            )
            return Response({"message": "Successfully logged out."})
        except TokenError:
            return Response(
                {"error": True, "message": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

# Self-service
class MeView(APIView):
    """GET /api/users/me/ - return the authenticated user's profile."""
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)


class ChangePasswordView(APIView):
    """POST /api/users/me/change-password/ — authenticated user changes own password."""
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password updated successfully."})


# Admin - User Management

class AdminUserListCreateView(generics.ListCreateAPIView):
    """
    GET /api/users/ - List all users (admin only)
    POST /api/Users/ - create a user with any role (admin only)
    """

    permission_classes = [permissions.IsAuthenticated, IsActiveUser, IsAdmin]
    queryset = User.objects.all().order_by("id")
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["role", "is_active"]
    search_fields = ["username", "email"]
    ordering_fields = ["username", "date_joined", "role"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminUserCreateSerialzer
        return AdminUserListSerializer


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/users/<id>/ - retrieve a user
    Patch  /api/users/<id>/ - update role / active status
    DELETE  /api/users/<id>/ - hard delete (admin only)
    """

    permission_classes = [permissions.IsAuthenticated, IsActiveUser, IsAdmin]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return AdminUserUpdateSerializer
        return AdminUserListSerializer
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response(
                {"error": True, "message": "You cannot delete your own account."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.delete()
        return Response({"message": "User deleted."}, status=status.HTTP_200_OK)


class AdminDeactivateUserView(APIView):
    """
    POST /api/users/<id>/deactivate/ - soft-disable an account (admin only)
    POST /api/users/<id>/activate/ - soft-enable an account (admin only)
    """
    permission_classes = [permissions.IsAuthenticated, IsActiveUser, IsAdmin]
    def post(self, request, pk, action):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": True, "message": "User not found."}, status=404)
        if user == request.user:
            return Response(
                {"error": True, "message": "You cannot change your own active status"},
                status= status.HTTP_400_BAD_REQUEST,
            )
        if action == "deactivate":
            user.is_active = False
            msg = "User deactivated."
        else:
            user.is_active = True
            msg = "User activated."
        user.save()
        return Response({"message": msg, "user": AdminUserListSerializer(user).data})


# class LogoutView(APIView):
#     """
#     POST /api/auth/logout/
#     Body: { "refresh": "<refresh token>" }
#     Blacklists the token so it cannot be used again.
#     """
#
#     permission_classes = [permissions.IsAuthenticated]
#     def post(self, request):
#         refresh_token = request.data.get("refresh")
#         if not refresh_token:
#             return Response(
#                 {"error": True, "message": "Refresh token is required."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         try:
#             token = UntypedToken(refresh_token)
#             BlacklistedToken.objects.get_or_create(
#                 jti=token["jti"],
#                 defaults={"token": refresh_token},
#             )
#             return Response({"message": "Successfully logged out."})
#         except TokenError:
#             return Response(
#                 {"error": True, "message": "Invalid or expired token."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )


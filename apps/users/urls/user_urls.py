
"""
User Management endpoint"""

from django.urls import path
from apps.users.views import (
    MeView,ChangePasswordView,AdminUserListCreateView,AdminUserDetailView,AdminDeactivateUserView,
)
urlpatterns = [
    # self-service
    path("me/", MeView.as_view(), name="user-me"),
    path("me/change-password/", ChangePasswordView.as_view(), name="user-change-password"),

    # Admin
    path("", AdminUserListCreateView.as_view(), name="user-list-create"),
    path("<int:pk>/", AdminUserListCreateView.as_view(), name="user-list-create"),
    path("<int:pk>/deactivate/", AdminDeactivateUserView.as_view(), name="user-deactivate"),
    path("<int:pk>/activate/", AdminDeactivateUserView.as_view(), name="user-activate"),
]
"""
User Serializers - registrations, profile, admin management.
"""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, Role

class RegisterSerializer(serializers.ModelSerializer):
    "Anyone can register; new accounts start as VIEWER"
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    """Read-only profile returned after login or GET /users/me/."""
    class Meta:
        model = User
        fields = ["id", "email", "username",  "role", "is_active", "date_joined"]
        read_only_fields = fields


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


#Admin Management
class  AdminUserCreateSerialzer(serializers.ModelSerializer):
    """Admin creates a user and can assign a role immediately."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    class Meta:
        model = User
        fields = ["id", "email", "username", "email", "role", "is_active", "date_joined", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Admin can change role active status, not password here."""
    class Meta:
        model = User
        fields = ["id", "email", "username",  "role", "is_active"]
    def validate_role(self, value):
        if value not in Role.values:
            raise serializers.ValidationError(f"Invalid role. Choose from: {Role.values}")
        return value


class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role",  "date_joined", "is_active",]
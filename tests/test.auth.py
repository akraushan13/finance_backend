"""
Tests for authentication endpoints.
"""
from rest_framework.test import APIClient
from django.test import TestCase

from apps.users.models import User, Role
from django.urls import reverse

from rest_framework import status


class AuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("auth-register")
        self.login_url    = reverse("auth-login")



    def test_register_mismatched_passwords(self):
        res = self.client.post(self.register_url, {
            "username":  "baduser",
            "email":     "bad@test.com",
            "password":  "StrongPass@99",
            "password2": "WrongPass@99",
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_creates_viewer(self):
        res = self.client.post(self.register_url, {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "StrongPass@99",
            "password2": "StrongPass@99",
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="newuser")
        self.assertEqual(user.role, Role.VIEWER)

    def test_login_wrong_password(self):
        User.objects.create_user(username="u2", email="u2@t.com", password="RealPass@1")
        res = self.client.post(self.login_url, {"username": "u2", "password": "wrong"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_returns_tokens(self):
        User.objects.create_user(username="loginuser", email="l@t.com", password="Pass@12345")
        res = self.client.post(self.login_url, {
            "username": "loginuser",
            "password": "Pass@12345",
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)



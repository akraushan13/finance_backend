"""
Tests for dashboard summary endpoints.
"""

from django.urls import reverse
from rest_framework.test import APIClient

from apps.records.models import FinancialRecord
from decimal import Decimal
from datetime import date
from django.test import TestCase
from rest_framework import status
from apps.users.models import User, Role


def auth_client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c

def make_user(username, role):
    return User.objects.create_user(
        username=username, email=f"{username}@test.com",
        password="TestPass@1", role=role,
    )



class DashboardAccessTests(TestCase):

    def setUp(self):
        self.admin   = make_user("dash_admin",   Role.ADMIN)
        self.analyst = make_user("dash_analyst", Role.ANALYST)
        self.viewer  = make_user("dash_viewer",  Role.VIEWER)

        # Create some records
        for i in range(5):
            FinancialRecord.objects.create(
                amount=Decimal("1000.00"), type="income",
                category="salary", date=date.today(), created_by=self.admin,
            )
            FinancialRecord.objects.create(
                amount=Decimal("300.00"), type="expense",
                category="food", date=date.today(), created_by=self.admin,
            )


    def test_overview_totals_correct(self):
        res = auth_client(self.admin).get(reverse("dashboard-overview"))
        self.assertAlmostEqual(res.data["total_income"],  5000.0)
        self.assertAlmostEqual(res.data["total_expense"], 1500.0)
        self.assertAlmostEqual(res.data["net_balance"],   3500.0)

    def test_viewer_can_see_overview(self):
        res = auth_client(self.viewer).get(reverse("dashboard-overview"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("total_income", res.data)
        self.assertIn("net_balance",  res.data)


    def test_viewer_cannot_see_categories(self):
        res = auth_client(self.viewer).get(reverse("dashboard-categories"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_analyst_can_see_monthly_trends(self):
        res = auth_client(self.analyst).get(reverse("dashboard-monthly"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("trends", res.data)

    def test_analyst_can_see_recent_activity(self):
        res = auth_client(self.analyst).get(reverse("dashboard-activity"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("activity", res.data)

    def test_analyst_can_see_categories(self):
        res = auth_client(self.analyst).get(reverse("dashboard-categories"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("categories", res.data)

    def test_unauthenticated_blocked_from_overview(self):
        res = APIClient().get(reverse("dashboard-overview"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

"""
Tests for financial records — CRUD + access control.
"""

from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User, Role
from apps.records.models import FinancialRecord

from decimal import Decimal
from datetime import date
from django.test import TestCase
from django.urls import reverse


def sample_record(user):
    return FinancialRecord.objects.create(
        amount=Decimal("500.00"),
        type="income",
        category="salary",
        date=date.today(),
        description="Test record",
        created_by=user,
    )

def make_user(username, role):
    return User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password="TestPass@1",
        role=role,
    )


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class RecordAccessControlTests(TestCase):

    def setUp(self):
        self.admin   = make_user("admin_u",   Role.ADMIN)
        self.analyst = make_user("analyst_u", Role.ANALYST)
        self.viewer  = make_user("viewer_u",  Role.VIEWER)
        self.list_url = reverse("record-list-create")

    # Read access

    def test_analyst_can_list_records(self):
        res = auth_client(self.analyst).get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_viewer_can_list_records(self):
        sample_record(self.admin)
        res = auth_client(self.viewer).get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_unauthenticated_cannot_list(self):
        res = APIClient().get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # Write access

    def test_admin_can_create_record(self):
        res = auth_client(self.admin).post(self.list_url, {
            "amount":      "1200.00",
            "type":        "income",
            "category":    "salary",
            "date":        str(date.today()),
            "description": "Admin created",
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_analyst_cannot_create_record(self):
        res = auth_client(self.analyst).post(self.list_url, {
            "amount": "100.00", "type": "expense",
            "category": "food", "date": str(date.today()),
        })
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_create_record(self):
        res = auth_client(self.viewer).post(self.list_url, {
            "amount": "100.00", "type": "expense",
            "category": "food", "date": str(date.today()),
        })
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)



    #  Update / Delete

    def test_viewer_cannot_delete_record(self):
        record = sample_record(self.admin)
        url = reverse("record-detail", kwargs={"pk": record.pk})
        res = auth_client(self.viewer).delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_record(self):
        record = sample_record(self.admin)
        url = reverse("record-detail", kwargs={"pk": record.pk})
        res = auth_client(self.admin).patch(url, {"description": "Updated"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_admin_soft_delete(self):
        record = sample_record(self.admin)
        url = reverse("record-detail", kwargs={"pk": record.pk})
        auth_client(self.admin).delete(url)
        record.refresh_from_db()
        self.assertTrue(record.is_deleted)

    # Filtering

    def test_filter_by_type(self):
        sample_record(self.admin)
        FinancialRecord.objects.create(
            amount=Decimal("200.00"), type="expense",
            category="food", date=date.today(), created_by=self.admin,
        )
        res = auth_client(self.viewer).get(self.list_url + "?type=income")
        self.assertEqual(res.status_code, 200)
        for item in res.data["results"]:
            self.assertEqual(item["type"], "income")

    # Validation

    def test_create_rejects_zero_amount(self):
        res = auth_client(self.admin).post(self.list_url, {
            "amount": "0.00", "type": "income",
            "category": "salary", "date": str(date.today()),
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejects_invalid_type(self):
        res = auth_client(self.admin).post(self.list_url, {
            "amount": "100.00", "type": "bonus",
            "category": "salary", "date": str(date.today()),
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


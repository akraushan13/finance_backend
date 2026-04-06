from django.db import models
import uuid
from django.core.validators import MinValueValidator
from django.conf import settings
from decimal import Decimal

# Create your models here.

"""
FinancialRecord model -core entity of the finance dashboard
"""

class ActiveRecordManager(models.Model):
    """Returns only non-deleted records"""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class FinancialRecord(models.Model):
    class Type(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"

    class Category(models.TextChoices):
        SALARY = "salary", "Salary"
        INVESTMENT = "investment", "Investment"
        FREELANCE = "freelance", "Freelance"
        UTILITIES = "utilities", "Utilities"
        HEALTHCARE = "healthcare", "Healthcare"
        FOOD = "food", "Food"
        RENT = "rent", "Rent"
        TRANSPORT = "transport", "Transport"
        EDUCATION = "education", "Education"
        ENTERTAINMENT = "entertainment", "Entertainment"
        TAX = "tax", "Tax"
        OTHER = "other", "Other"

    # Identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Core field
    amount = models.DecimalField(max_digits=14, decimal_places=2,
                                 validators=[MinValueValidator(0.01)],
                                 )
    category = models.CharField(max_length=20, choices=Category.choices, db_index=True)
    type = models.CharField(max_length=10, choices=Type.choices, db_index=True)
    date = models.DateField(db_index=True)
    description = models.TextField(blank=True, default="")

    # Ownership / audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="records",
    )

    # soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active = ActiveRecordManager()

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["type", "date"]),
            models.Index(fields=["category", "date"]),
        ]

    def __str__(self):
        return f"{self.type.upper()} | {self.category} | {self.amount} | {self.date}"

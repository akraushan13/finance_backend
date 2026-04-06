from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class Role(models.TextChoices):
    VIEWER = "viewer", "Viewer"
    ANALYST = "analyst", "Analyst"
    ADMIN = "admin", "Admin"

class User(AbstractUser):
    """
    Extends Django AbstractUser to add:
     role: Viewer, Analyst, Admin
     is_active: reused from AbstracrtUser (Soft-disable account)
    """

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VIEWER,
        db_index=True
    )

    # Keep email unique so it can be as an alternate login identifier
    email = models.EmailField(unique=True)

    class Meta:
        ordering = ["username"],
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ANALYST



    @property
    def is_analyst(self) -> bool:
        return self.role == self.Role.ANALYST

    @property
    def is_viewer(self) -> bool:
        return self.role == self.Role.VIEWER
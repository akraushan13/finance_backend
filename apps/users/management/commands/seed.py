import random
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from apps.users.models import User, Role
from apps.records.models import FinancialRecord


class Command(BaseCommand):
    help = "Seed the database with sample users and financial records"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating users...")

        admin = self._make_user("admin",   "admin@finance.dev",   "Admin@1234",   Role.ADMIN)
        analyst = self._make_user("analyst", "analyst@finance.dev", "Analyst@1234", Role.ANALYST)
        self._make_user("viewer",  "viewer@finance.dev",  "Viewer@1234",  Role.VIEWER)

        INCOME_CATS  = ["salary", "investment", "freelance"]
        EXPENSE_CATS = ["food", "rent", "utilities", "healthcare",
                        "transport", "education", "entertainment", "tax", "other"]

        self.stdout.write("Creating financial records...")
        records = []
        for i in range(50):
            rec_type = random.choice(["income", "expense"])
            category = random.choice(
                INCOME_CATS if rec_type == "income" else EXPENSE_CATS
            )
            records.append(FinancialRecord(
                amount=Decimal(str(round(random.uniform(50, 5000), 2))),
                type=rec_type,
                category=category,
                date=date.today() - timedelta(days=random.randint(0, 365)),
                description=f"Seeded {rec_type} record #{i + 1}",
                created_by_id=random.choice([admin, analyst]).pk,
            ))

        FinancialRecord.objects.bulk_create(records)
        self.stdout.write(self.style.SUCCESS(f"  Created {len(records)} records."))
        self.stdout.write(self.style.SUCCESS("\nDone!"))
        self.stdout.write("  admin    / Admin@1234")
        self.stdout.write("  analyst  / Analyst@1234")
        self.stdout.write("  viewer   / Viewer@1234")

    def _make_user(self, username, email, password, role):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "role": role},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f"  Created {role}: {username}")
        else:
            self.stdout.write(f"  Already exists: {username}")
        return user
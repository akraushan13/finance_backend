"""
Dashboard service layer - all aggregation and analytics logic lives here,
keeping views thin and this layer independently testable.
"""
from decimal import Decimal
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth, TruncWeek, TruncDate
from django.utils import timezone
from datetime import timedelta, date

from apps.records.models import FinancialRecord

# Type aliases
INCOME = FinancialRecord.Type.INCOME
EXPENSE = FinancialRecord.Type.EXPENSE


def _active():
    """Shorthand - only non-deleted records"""
    return FinancialRecord.objects.filter(is_deleted=False)


# 1. Overview summary

def get_overview(date_from=None, date_to=None) -> dict:
    """
    Returns total income, total expenses, net balance, and record counts
    for the given optional date window.
    """
    qs = _active()
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    agg = qs.aggregate(
        total_income=Sum("amount", filter=Q(type=INCOME)),
        total_expense=Sum("amount", filter=Q(type=EXPENSE)),
        income_count=Count("id", filter=Q(type=INCOME)),
        expense_count=Count("id", filter=Q(type=EXPENSE)),
        total_records=Count("id"),
    )
    income = agg["total_income"] or Decimal("0.00")
    expense = agg["total_expense"] or Decimal("0.00")

    return {
        "total_income": float(income),
        "total_expense": float(expense),
        "net_balance": float(income - expense),
        "income_count": agg["income_count"],
        "expense_count": agg["expense_count"],
        "total_records": agg["total_records"],
        "date_from": str(date_from) if date_from else None,
        "date_to": str(date_to) if date_to else None,
    }

# 2. Category breakdown
def get_category_breakdown(record_type=None, date_from=None, date_to=None) -> list:
    """ returns per-category totals and counts
    Optionally filter by record_type (income |  expense)."""
    qs = _active()
    if record_type:
        qs = qs.filter(type=record_type)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    rows = (
        qs.values("category")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("-total")
    )
    return [
        {
            "category": r["category"],
            "total": float(r["total"]),
            "count": r["count"]
        }
        for r in rows
    ]


# 3. Monthly trends
def get_monthly_trends(months: int = 12) -> list:
    """
    Returns month-by-month income vs expense totals for the last `months` months.
    """
    cutoff = date.today().replace(day=1) - timedelta(days=30 * (months - 1))
    rows = (
        _active()
        .filter(date__gte=cutoff)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(
            income=Sum("amount", filter=Q(type=INCOME)),
            expense=Sum("amount", filter=Q(type=EXPENSE)),
        )
        .order_by("month")
    )
    return [
        {
            "month": r["month"].strftime("%Y-%m"),
            "income": float(r["income"] or 0),
            "expense": float(r["expense"] or 0),
            "net": float((r["income"] or 0) - (r["expense"] or 0)),
        }
        for r in rows
    ]


#  4. Weekly_trends
def get_weekly_trends(weeks: int=12) -> list:
    """
    Return week-by-week income vs expense totals for the last "week" weeks.
    """
    cutoff = date.today() - timedelta(weeks=weeks)
    rows = (
        _active()
        .filter(date__gte=cutoff)
        .annotate(week=TruncWeek("date"))
        .values("week")
        .annotate(
            income=Sum("amount", filter=Q(type=INCOME)),
            expense=Sum("amount", filter=Q(type=EXPENSE)),
        )
        .order_by("week")
    )
    return [
        {
            "week_start": r["week"].strftime("%Y-%m-%d"),
            "income": float(r["income"] or 0),
            "expense": float(r["expense"] or 0),
            "net": float((r["income"] or 0) - (r["expense"] or 0)),
        }
        for r in rows
    ]

# 5. Recent activity

def get_recent_activity(limit: int = 10) -> list:
    """Returns the `limit` most recent records as lightweight dicts."""
    records = (
        _active()
        .select_related("created_by")
        .order_by("-date", "-created_at")[:limit]
    )
    return [
        {
            "id": str(r.id),
            "amount": float(r.amount),
            "type": r.type,
            "category": r.category,
            "date": str(r.date),
            "description": r.description,
            "created_by": r.created_by.username if r.created_by else None,
        }
        for r in records
    ]

# 6. Daily spending (last n days)

def get_daily_spending(days: int = 30) -> list:
    """Day-by-day expense totals for the last `days` days."""
    cutoff = date.today() - timedelta(days=days)

    rows = (
        _active()
        .filter(type=EXPENSE, date__gte=cutoff)
        .annotate(day=TruncDate("date"))
        .values("day")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("day")
    )

    return [
        {
            "date":r["day"].strftime("%Y-%m-%d"),
            "total": float(r["total"]),
            "count": r["count"],
        }
        for r in rows
    ]

# 7. Top categories

def get_top_categories(record_type: str = EXPENSE, limit: int = 5) -> list:
    """Returns the top `limit` categories by total amount for a given type."""
    return get_category_breakdown(record_type=record_type)[:limit]
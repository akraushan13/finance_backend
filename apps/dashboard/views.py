"""
Dashboard API views.

Access matrix:
    VIEWER -> overview only
    ANALYST -> all dashboard endpoints
    ADMIN -> all dashboard endpoints
"""
from datetime import date as date_type
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.core.permissions import IsAnalystOrAbove, IsActiveUser
from . import services


def _parse_date(value: str | None):
    """Safely parse a YYYY-MM-DD string or return None."""
    if not value:
        return None
    try:
        return date_type.fromisoformat(value)
    except ValueError:
        return None


class OverviewView(APIView):
    """
    GET /api/dashboard/overview/
    All authenticated users (viewer and above).
    Query params:

    date_from  YYYY-MM-DD
    date_to    YYYY-MM-DD
    """
    permissions_classes = [permissions.IsAuthenticated, IsActiveUser]

    @extend_schema(
        parameters=[
            OpenApiParameter("date_from", str, description="Start date YYYY-MM-DD"),
            OpenApiParameter("date_to", str, description="End date YYYY-MM-DD"),
        ]
    )
    def get(self, request):
        date_from = _parse_date(request.query_params.get("date_from"))
        date_to = _parse_date(request.query_params.get("date_to"))
        data = services.get_overview(date_from=date_from, date_to=date_to)
        return Response(data)


class CategoryBreakdownView(APIView):
    """
    GET /api/dashboard/categories/
    Analyst and above.

    Query params:
    type       income | expense
    date_from  YYYY-MM-DD
    date_to    YYYY-MM-DD
    """
    permission_classes = [permissions.IsAuthenticated, IsActiveUser, IsAnalystOrAbove]

    def get(self,request):
        record_type = request.query_params.get("type")
        date_from = _parse_date(request.query_params.get("date_from"))
        date_to = _parse_date(request.query_params.get("date_to"))
        data = services.get_category_breakdown(
            record_type=record_type, date_from=date_from, date_to=date_to
        )
        return Response({"categories": data, "count": len(data)})


class MonthlyTrendsView(APIView):
    """
    GET /api/dashboard/trends/monthly/
    Analyst and above.

    Query params:
    months  int (default 12)
    """
    permission_classes = [permissions.IsAuthenticated, IsActiveUser, IsAnalystOrAbove]

    def get(self, request):
        try:
            months = int(request.query_params.get("months", 12))
            months = min(max(months, 1), 60)
        except (ValueError, TypeError):
            months = 12
        data = services.get_monthly_trends(months=months)
        return Response({"months": months, "trends": data})


class WeeklyTrendsView(APIView):
    """
    Get /api/dashboard/trends/weekly/
    Analyst and above.

    Query params:
    weeks  int (default 12)
    """
    permission_classes = [permissions.IsAuthenticated, IsActiveUser, IsAnalystOrAbove]

    def get(self, request):
        try:
            weeks = int(request.query_params.get("weeks", 12))
            weeks = min(max(weeks, 1), 52)
        except (ValueError, TypeError):
            weeks = 12
        data = services.get_weekly_trends(weeks=weeks)
        return Response({"weeks": weeks, "trends": data})


class RecentActivityView(APIView):
    """
    GET /api/dashboard/activity/
    Analyst and above.

    Query params:
        limit  int (default 10, max 50)
    """
    permission_classes = [permissions.IsAuthenticated, IsActiveUser, IsAnalystOrAbove]

    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 10))
            limit = min(max(limit, 1), 50)
        except (ValueError, TypeError):
            limit = 10
        data = services.get_recent_activity(limit=limit)
        return Response({"activity": data, "count": len(data)})


class DailySpendingView(APIView):
    """
    GET /api/dashboard/spending/daily/
    Analyst and above.

    Query params:
    days  int (default 30, max 365)
    """
    permission_classes = [permissions.IsAuthenticated, IsActiveUser, IsAnalystOrAbove]

    def get(self, request):
        try:
            days = int(request.query_params.get("days", 30))
            days = min(max(days, 1), 365)
        except (ValueError, TypeError):
            days = 30
        data = services.get_daily_spending(days=days)
        return Response({"days": days, "spending": data})


class TopCategoriesView(APIView):
    """
    GET /api/dashboard/categories/top/
    Analyst and above.

    Query params:
    type   income | expense (default expense)
    limit  int (default 5)
    """
    permission_classes = [permissions.IsAuthenticated, IsActiveUser, IsAnalystOrAbove]

    def get(self, request):
        record_type = request.query_params.get("type", "expense")
        try:
            limit = int(request.query_params.get("limit", 5))
            limit = min(max(limit, 1), 20)
        except (ValueError, TypeError):
            limit = 5
        data = services.get_top_categories(record_type=record_type, limit=limit)
        return Response({"type": record_type, "top_categories": data})
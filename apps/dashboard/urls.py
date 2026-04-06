from django.urls import path
from .views import (
    OverviewView,
    CategoryBreakdownView,
    MonthlyTrendsView,
    WeeklyTrendsView,
    RecentActivityView,
    DailySpendingView,
    TopCategoriesView
)

urlpatterns = [
    path("overview/", OverviewView.as_view(), name="dashboard-overview"),
    path("categories/", CategoryBreakdownView.as_view(), name="dashboard-categories"),
    path("categories/top/", TopCategoriesView.as_view(), name="dashboard-top-categories"),
    path("trends/", MonthlyTrendsView.as_view(), name="dashboard-monthly"),
    path("trends/weekly/", WeeklyTrendsView.as_view(), name="dashboard-weekly"),
    path("activity/", RecentActivityView.as_view(), name="dashboard-activity"),
    path("spending/daily", DailySpendingView.as_view(), name="dashboard-daily"),
]
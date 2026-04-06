from django.urls import path
from .views import (
FinancialRecordDetailView, FinancialRecordListCreateView, BulkCreateRecordsView, RestoreRecordView
)

urlpatterns = [
    path("", FinancialRecordListCreateView.as_view(), name="record-list-create"),
    path("bulk/", BulkCreateRecordsView.as_view(), name="record-bulk-create"),
    path("<uuid:pk>/restore/", RestoreRecordView.as_view(), name="record-restore"),
    path("<uuid:pk>/", FinancialRecordDetailView.as_view(), name="record-detail"),
]
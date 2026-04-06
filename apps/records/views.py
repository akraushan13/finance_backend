"""
Financial record CRUD views with role-based access control.
Access matrix:
  VIEWER -> GET list, GET detail
  ANALYST  -> GET list, GET detail
  ADMIN    -> GET list, GET detail
"""
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.permissions import IsAdmin, IsAnalystOrAbove, IsActiveUser
from .filters import FinancialRecordFilter
from .models import FinancialRecord
from .serializers import (
    FinancialRecordSerializer,
    FinancialRecordListSerializer,
    BulkCreateSerializer
)

# Helper Functions

def get_active_record_or_404(pk):
    try:
        return FinancialRecord.active.get(pk=pk)
    except FinancialRecord.DoesNotExist:
        return None

class FinancialRecordListCreateView(generics.ListCreateAPIView):
    """
    GET /api/records/ -> all roles (viewer, analyst, admin)
    POST /api/records/ -> admin only
    """

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = FinancialRecordFilter
    search_fields = ["description", "category"]
    ordering_fields = ["date", "amount", "created_at", "category", "type"]
    ordering = ["-date"]

    def get_queryset(self):
        return FinancialRecord.objects.filter(is_deleted=False)

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsActiveUser(), IsAdmin()]
        return [permissions.IsAuthenticated(), IsActiveUser()]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return FinancialRecordListSerializer
        return FinancialRecordSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "Record created.", "record": serializer.data},
            status=status.HTTP_201_CREATED,
        )


# Retrieve, update, delete
class FinancialRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/record/<id>/ -> all roles (viewer, analyst, admin)
    PATCH  /api/record/<id>/ -> admin only
    DELETE /api/record/<id>/ -> admin only (soft delete by default)
    """

    serializer_class = FinancialRecordSerializer
    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [permissions.IsAuthenticated(), IsActiveUser(), IsAdmin()]
        return [permissions.IsAuthenticated(), IsActiveUser()]

    def get_object(self):
        record = FinancialRecord.objects.filter(
            pk=self.kwargs["pk"], is_deleted=False
        ).first()
        if record is None:
            from rest_framework.exceptions import NotFound
            raise NotFound("Record not found or has been deleted.")
        self.check_object_permissions(self.request, record)
        return record

    def get_queryset(self):
        return FinancialRecord.objects.filter(is_deleted=False)


    def partial_update(self,request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Soft Delete by default; pass ?hard=true for permanent deletion."""
        record = self.get_object()
        hard = request.query_params.get("hard", "").lower() == "true"
        if hard:
            record.delete()
            return Response( {"message":"Record deleted"}, status=status.HTTP_204_NO_CONTENT)
        record.is_deleted = True
        record.deleted_at = timezone.now()
        record.save()
        return Response({"message": "Record permanently deleted."}, status=200)

class RestoreRecordView(APIView):
    """
    POST /api/records/<id>/restore/ - un-delete a soft-deleted record (admin only).
    """
    permission_classes = [permissions.IsAuthenticated, IsActiveUser, IsAdmin]
    def post(self, request, pk):
        try:
            record = FinancialRecord.objects.get(pk=pk, is_deleted=True)
        except FinancialRecord.DoesNotExist:
            return Response(
                {"error": True, "message": "Deleted record not found."},
                status=404,
            )
        record.is_deleted = False
        record.deleted_at = None
        record.save()
        return Response(
            {"message": "Record restored.", "record": FinancialRecordSerializer(record).data}
        )

class BulkCreateRecordsView(APIView):
    """
    POST /api/records/bulk/
    Atomically create multiple records in a single request (admin only).
    Body: { "records": [ { ...record fields }, ... ] }
    """

    permission_classes = [permissions.IsAuthenticated, IsActiveUser, IsAdmin]

    def post(self, request):
        serializer = BulkCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        created = serializer.save()
        return Response(
            {"message": f"{len(created)} records created.", "count": len(created)},
            status=status.HTTP_201_CREATED,
        )


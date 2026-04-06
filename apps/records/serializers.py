"""
Financial record serializers.
"""
from venv import create

from rest_framework import serializers
from .models import FinancialRecord

class FinancialRecordSerializer(serializers.ModelSerializer):
    """Full read/write serializer used by admin and analysts."""
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = FinancialRecord
        fields = [
            "id", "amount", "type", "category", "date",
            "description", "created_by_username",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by_username", "created_at", "updated_at"]

    def validate_category(self, value):
        if value not in FinancialRecord.Category.values:
            raise serializers.ValidationError(
                f"Invalid type. Choose from: {FinancialRecord.Category.values}"
            )
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
    def validate_type(self, value):
        if value not in FinancialRecord.Type.values:
            raise serializers.ValidationError(
                f"Invalid type. Choose from: {FinancialRecord.Type.values}"
            )
        return value

class FinancialRecordListSerializer(serializers.ModelSerializer):
    """Lightweight serialzer for list views- omits heavy fields."""

    class Meta:
        model = FinancialRecord
        fields = ["id", "amount", "category", "type", "date", "description"]

class BulkCreateSerializer(serializers.Serializer):
    """Wraps a list of records for atomic bulk creation."""
    records = FinancialRecordListSerializer(many=True)
    def create(self, validated_data):
        user = self.context["request"].user
        items = validated_data["records"]
        objects = [
            FinancialRecord(**item, created_by=user)
            for item in items
        ]
        return FinancialRecord.objects.bulk_create(objects)
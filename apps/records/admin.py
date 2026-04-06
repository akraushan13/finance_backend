from django.contrib import admin
from .models import FinancialRecord

# Register your models here.
@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "amount", "category", "date", "is_deleted"]
    list_filter = ["category", "type", "is_deleted"]
    search_fields = ["description", "category",]
    date_hierarchy = "date"
    readonly_fields = ["id", "created_at", "updated_at"]
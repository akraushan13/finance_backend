"""
Filterset for FinancialRecord - supports date reange, type, category, amount range.
"""
import django_filters
from .models import FinancialRecord

class FinancialRecordFilter(django_filters.FilterSet):
    # Exact Matches
    type = django_filters.ChoiceFilter(choices=FinancialRecord.Type.choices)
    category = django_filters.ChoiceFilter(choices=FinancialRecord.Category.choices)
    amount_min = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")


    class Meta:
        model = FinancialRecord
        fields = ["type", "category", "date_to", "date_from", "amount_min", "amount_max"]
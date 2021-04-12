from django_filters import FilterSet, CharFilter, DateRangeFilter, DateFilter
from main.models import Document


class DocumentFilter(FilterSet):
    title_name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Document
        fields = ['title_name']

from django_filters import FilterSet, CharFilter, DateRangeFilter, DateFilter
from main.models import Institution, Document


class InstitutionFilter(FilterSet):
    """Filter to filter an institution table"""
    institution_name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Institution
        fields = ['institution_name']


class DocumentFilter(FilterSet):
    """Filter to filter a document table"""
    title_name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Document
        fields = ['title_name']

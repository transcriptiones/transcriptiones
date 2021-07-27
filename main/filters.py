from django.db.models import Q
from django import forms
from django_filters import FilterSet, CharFilter, DateRangeFilter, DateFilter, BooleanFilter, MultipleChoiceFilter, \
    ChoiceFilter
from main.models import Institution, RefNumber, Document, User


class InstitutionFilter(FilterSet):
    """Filter to filter an institution table"""
    institution_name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Institution
        fields = ['institution_name']


class RefNumberFilter(FilterSet):
    """Filter to filter a reference number table"""
    ref_number_name = CharFilter(method='multi_filter')

    class Meta:
        model = RefNumber
        fields = ['ref_number_name']

    def multi_filter(self, queryset, name, value):
        return queryset.filter(Q(ref_number_name__icontains=value) | Q(ref_number_title__icontains=value))


class DocumentFilter(FilterSet):
    """Filter to filter a document table"""
    title_name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Document
        fields = ['title_name']


class UserFilter(FilterSet):
    """Filter to filter a user table"""
    STATUS_CHOICES = (
        (0, 'User'),
        (1, 'Staff'),
        (2, 'Admin'),
    )

    username = CharFilter(lookup_expr='icontains')
    user_state = ChoiceFilter(choices=STATUS_CHOICES)

    class Meta:
        model = User
        fields = ['username', ]
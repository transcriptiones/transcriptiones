from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet, CharFilter, DateRangeFilter, DateFilter, BooleanFilter, MultipleChoiceFilter, \
    ChoiceFilter, ModelChoiceFilter, DateFromToRangeFilter
from main.models import Institution, RefNumber, Document, User, SourceType, Author


class SourceTypeFilter(FilterSet):
    """Filter to filter a source type table"""
    institution_name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = SourceType
        fields = ['institution_name']


class AuthorFilter(FilterSet):
    """Filter to filter a source type table"""
    author_name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Author
        fields = ['author_name']


class InstitutionFilter(FilterSet):
    """Filter to filter an institution table"""
    institution_name = CharFilter(lookup_expr='icontains')
    city = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Institution
        fields = ['institution_name', 'city', 'country']


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
    place_name = CharFilter(lookup_expr='icontains')
    doc_start_date = DateFromToRangeFilter()
    source_type = ModelChoiceFilter(queryset=SourceType.objects.all().order_by('type_name'))

    class Meta:
        model = Document
        fields = ['title_name', 'source_type', 'place_name', 'doc_start_date']


class UserFilter(FilterSet):
    """Filter to filter a user table"""
    STATUS_CHOICES = (
        (0, _('User')),
        (1, _('Staff')),
        (2, _('Admin')),
    )

    username = CharFilter(lookup_expr='icontains')
    user_state = ChoiceFilter(choices=STATUS_CHOICES)

    class Meta:
        model = User
        fields = ['username', ]
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django_tables2 import MultiTableMixin, SingleTableMixin
from django_filters.views import FilterView

import main.model_info as m_info
from main.models import Institution, RefNumber, Document
from main.tables import TitleValueTable, RefNumberTable, DocumentTable, InstitutionTable
from main.filters import InstitutionFilter, RefNumberFilter, DocumentFilter


class InstitutionListView(SingleTableMixin, FilterView):
    """Creates a list view for all institutions.
    Features a filter to filter the institution table."""

    model = Institution
    table_class = InstitutionTable
    filterset_class = InstitutionFilter
    template_name = "main/details/institution_list.html"

    def get_queryset(self):
        return Institution.objects.all().order_by('institution_name')
    # TODO sorted queryset by name


class InstitutionDetailView(MultiTableMixin, DetailView):
    """View to show details of institutions and list all reference numbers of this institution."""
    model = Institution
    slug_field = 'institution_slug'
    slug_url_kwarg = 'inst_slug'
    my_filter = None

    table_pagination = {
        "per_page": 20
    }
    template_name = "main/details/institution_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.my_filter = RefNumberFilter(request.GET, RefNumber.objects.filter(holding_institution=self.get_object()))
        return super(InstitutionDetailView, self).dispatch(request, *args, **kwargs)

    def get_tables(self):
        institution = self.get_object()
        data = m_info.get_institution_info(institution)

        tables = [
            TitleValueTable(data=data),
            RefNumberTable(self.my_filter.qs)
        ]
        return tables

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.my_filter
        return context


class RefNumberDetailView(MultiTableMixin, DetailView):
    """View to show details of institutions and list all reference numbers of this institution"""

    model = RefNumber
    slug_field = 'ref_number_slug'
    slug_url_kwarg = 'ref_slug'
    my_filter = None
    table_pagination = {
        "per_page": 20
    }

    template_name = "main/details/ref_number_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.my_filter = DocumentFilter(request.GET, Document.objects.filter(parent_ref_number=self.get_object()))
        return super(RefNumberDetailView, self).dispatch(request, *args, **kwargs)

    def get_tables(self):
        ref_number = self.get_object()
        data = m_info.get_ref_number_info(ref_number)

        tables = [
            TitleValueTable(data=data),
            DocumentTable(self.my_filter.qs),
        ]
        return tables

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.my_filter
        return context


class DocumentDetailView(MultiTableMixin, DetailView):
    """View to display Document. Accepts optional version number to display legacy version"""
    model = Document
    slug_field = 'document_slug'
    slug_url_kwarg = 'doc_slug'

    template_name = "main/details/document_detail.html"

    def get_object(self):
        institution = self.kwargs.get('inst_slug')
        ref_number = self.kwargs.get('ref_slug')
        document = self.kwargs.get('doc_slug')
        queryset = Document.all_objects.filter(parent_ref_number__holding_institution__institution_slug=institution)
        queryset = queryset.filter(parent_ref_number__ref_number_slug=ref_number)
        queryset = queryset.filter(document_slug=document)
        print(queryset)

        # if url specifies version_number, get this specific version, else get the active version
        if 'version_nr' in self.kwargs:
            version = self.kwargs.get('version_nr')
        else:
            version = queryset.get(active=True).version_number

        return get_object_or_404(queryset, version_number=version)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # if view should display legacy version, add newest version to context
        if 'version_nr' in self.kwargs:
            newest = self.get_object().get_versions().latest()
            context['newest'] = newest

        return context

    def get_tables(self):
        document = self.get_object()

        tables = [
            TitleValueTable(data=m_info.get_document_info_overview(document)),
            TitleValueTable(data=m_info.get_document_info_metadata(document)),
            TitleValueTable(data=m_info.get_document_info_manuscript(document)),
            TitleValueTable(data=m_info.get_document_info_comments(document)),
        ]

        return tables


class DocumentHistoryView(DetailView):
    """View to display version history of a DocumentTitle object"""

    model = Document
    template_name = "main/details/document_history.html"

    def get_object(self):
        institution = self.kwargs.get('inst_slug')
        ref_number = self.kwargs.get('ref_slug')
        document = self.kwargs.get('doc_slug')
        queryset = Document.objects.filter(parent_ref_number__holding_institution__institution_slug=institution)
        queryset = queryset.filter(parent_ref_number__ref_number_slug=ref_number)
        return get_object_or_404(queryset, document_slug=document)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        versions = self.model.get_versions(self.get_object())
        context['versions'] = versions
        return context
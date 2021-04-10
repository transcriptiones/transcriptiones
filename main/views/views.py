from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, ListView, View
from django.views.generic.detail import SingleObjectMixin
from django_tables2 import SingleTableMixin, MultiTableMixin

from main.models import Institution, RefNumber, Document
from main.tables import TitleValueTable, RefNumberTable, DocumentTable


class InstitutionListView(ListView):
    """Creates a list view for all instituions. """
    model = Institution
    queryset = Institution.objects.order_by('city', 'institution_name')
    template_name = "main/lists/institution_list.html"
    context_object_name = "institutions"


class InstitutionDetailView(MultiTableMixin, DetailView):
    """View to show details of institutions and list all reference numbers of this institution"""
    model = Institution
    slug_field = 'institution_slug'
    slug_url_kwarg = 'inst_slug'

    table_pagination = {
        "per_page": 20
    }

    template_name = "main/details/institution_detail.html"

    def get_tables(self):
        institution = self.get_object()
        data = [
            {'title': institution._meta.get_field('street').verbose_name,
             'value': institution.street},
            {'title': f"{institution._meta.get_field('zip_code').verbose_name} / {institution._meta.get_field('city').verbose_name}",
             'value': f"{institution.zip_code} / {institution.city}"},
            {'title': institution._meta.get_field('country').verbose_name,
             'value': institution.country.name},
            {'title': institution._meta.get_field('site_url').verbose_name,
             'value': mark_safe(f'<a href="{institution.site_url}" target="_blank">{institution.site_url}</a>')}
        ]

        tables = [
            TitleValueTable(data=data),
            RefNumberTable(RefNumber.objects.filter(holding_institution=institution))
        ]
        return tables


class RefNumberDetailView(MultiTableMixin, DetailView):
    """View to show details of institutions and list all reference numbers of this institution"""

    model = RefNumber
    slug_field = 'ref_number_slug'
    slug_url_kwarg = 'ref_slug'

    table_pagination = {
        "per_page": 20
    }

    template_name = "main/details/ref_number_detail.html"


    def get_tables(self):
        ref_number = self.get_object()
        data = [
            {'title': ref_number._meta.get_field('holding_institution').verbose_name,
             'value': ref_number.holding_institution},
            {'title': ref_number._meta.get_field('ref_number_name').verbose_name,
             'value': ref_number.ref_number_name},
            {'title': ref_number._meta.get_field('ref_number_title').verbose_name,
             'value': ref_number.ref_number_title},
            {'title': ref_number._meta.get_field('collection_link').verbose_name,
             'value': mark_safe(f'<a href="{ref_number.collection_link}" target="_blank">{ref_number.collection_link}</a>')}
        ]

        tables = [
            TitleValueTable(data=data),
            DocumentTable(Document.objects.filter(parent_ref_number=ref_number)),
        ]
        return tables


class DocumentDetailView(MultiTableMixin, DetailView):
    """View to display DocumentTitle. Accepts optional version number to display legacy version"""
    model = Document
    slug_field = 'document_slug'
    slug_url_kwarg = 'doc_slug'

    template_name = "main/details/document_detail.html"

    def get_object(self):
        institution = self.kwargs.get('inst_slug')
        ref_number = self.kwargs.get('ref_slug')
        document = self.kwargs.get('doc_slug')

        queryset = Document.all_objects.filter(parent_institution__institution_slug=institution)
        queryset = queryset.filter(parent_ref_number__ref_number_slug=ref_number)
        queryset = queryset.filter(document_slug=document)

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
        data = document.get_card_data()

        tables = [TitleValueTable(data=data[i]) for i in range(len(data))]

        return tables


def test(request):
    return render(request, 'main/test.html')

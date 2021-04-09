from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, ListView

from .models import Institution, RefNumber, Document


class InstitutionListView(ListView):
    """Creates a list view for all instituions. """
    model = Institution
    queryset = Institution.objects.order_by('city', 'institution_name')
    template_name = "main/lists/institution_list.html"
    context_object_name = "institutions"


class InstitutionDetailView(DetailView):
    """View to show details of institutions and list all reference numbers of this institution"""
    model = Institution
    slug_field = 'institution_slug'
    slug_url_kwarg = 'inst_slug'
    template_name = "main/details/institution_detail.html"


class RefNumberDetailView(DetailView):
    """View to show details of institutions and list all reference numbers of this institution"""
    model = RefNumber
    template_name = "main/details/ref_number_detail.html"

    def get_object(self):
        institution = self.kwargs.get('inst_slug')
        ref_number = self.kwargs.get('ref_slug')
        queryset = RefNumber.objects.filter(holding_institution__institution_slug=institution)
        return get_object_or_404(queryset, ref_number_slug=ref_number)


class DocumentDetailView(DetailView):
    """View to display DocumentTitle. Accepts optional version number to display legacy version"""
    model = Document
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


def test(request):
    return render(request, 'main/test.html')

from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, ListView

from .models import Institution, RefNumber


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
    template_name = "display/refnumberdetail.html"

    def get_object(self):
        institution = self.kwargs.get('inst_slug')
        ref_number = self.kwargs.get('ref_slug')
        queryset = RefNumber.objects.filter(holding_institution__institution_slug=institution)
        return get_object_or_404(queryset, refnumber_slug=ref_number)


def test(request):
    return render(request, 'main/test.html')

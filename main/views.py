from django.shortcuts import render
from django.http.response import HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, ListView

from .models import Institution


class InstitutionListView(ListView):
    """Creates a list view for all instituions. """
    model = Institution
    queryset = Institution.objects.order_by('city', 'institution_name')
    template_name = "main/lists/institution_list.html"
    context_object_name = "institutions"


def test(request):
    # return HttpResponse(_('Test'))
    return render(request, 'main/test.html')

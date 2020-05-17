from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import View
from django.views.generic import DetailView, ListView

from transcripta.transcripts.models import Institution, RefNumber, DocumentTitle

#View to list all institutions

class InstitutionListView(ListView):
    model = Institution
    queryset = Institution.objects.order_by('city', 'institution_name')
    template_name = "display/institutionlist.html"
    context_object_name = "institutions"



#View to show details of institutions and list all reference numbers of this institution

class InstitutionDetailView(DetailView):
    model = Institution
    slug_field = 'institution_slug'
    slug_url_kwarg = 'instslug'
    template_name = "display/institutiondetail.html"



#View to show details of reference number and list all documents within it

class RefNumberDetailView(DetailView):
    model = RefNumber
    template_name = "display/refnumberdetail.html"
    
    def get_object(self):
        institution = self.kwargs.get('instslug')
        refnumber = self.kwargs.get('refslug')
        queryset = RefNumber.objects.filter(holding_institution__institution_slug = institution)
        return get_object_or_404(queryset, refnumber_slug = refnumber)



class DocumentTitleDetailView(DetailView):
    model = DocumentTitle
    template_name = "display/documenttitledetail.html"

    def get_object(self):
        institution = self.kwargs.get('instslug')
        refnumber = self.kwargs.get('refslug')
        document = self.kwargs.get('docslug')
        queryset = DocumentTitle.objects.filter(parent_institution__institution_slug = institution)
        queryset = queryset.filter(parent_refnumber__refnumber_slug = refnumber)
        return get_object_or_404(queryset, document_slug = document)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.get_object().start_month:
            context['start_month_name'] = self.model.MonthChoices.names[self.get_object().start_month - 1]
        if self.get_object().end_month:
            context['end_month_name'] = self.model.MonthChoices.names[self.get_object().end_month - 1]
        return context

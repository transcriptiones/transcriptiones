from django.shortcuts import render
from django.views.generic import TemplateView, FormView, ListView

from transcripta.upload.models import DocumentTitle

class SearchView(TemplateView):
    template_name = "search/searchview.html"

class ResultsView(ListView):
    
    def get_queryset(self):
        return DocumentTitle.objects.search(self.request.GET)


    template_name = "search/resultsview.html"
    context_object_name = "results"
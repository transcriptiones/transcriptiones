from django.shortcuts import render
from django.views.generic import TemplateView, FormView, ListView

from transcripta.transcripts.forms.search import SearchForm
from transcripta.transcripts.models import DocumentTitle


class SearchView(FormView):
    template_name = "search/searchview.html"
    form_class = SearchForm
    success_url = 'results'

    def form_valid(self, form):
        print(form.cleaned_data)
        return super(SearchView, self).form_valid(form)


class ResultsView(ListView):

    def get_queryset(self):
        return DocumentTitle.objects.search(self.request.GET)

    template_name = "search/resultsview.html"
    context_object_name = "results"
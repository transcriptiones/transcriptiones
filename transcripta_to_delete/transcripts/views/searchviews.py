from django.views.generic import FormView, ListView

from transcripta.transcripts.documents import TranscriptionDocument
from transcripta.transcripts.forms.search import SearchForm, Attribute

FULLTEXT_FIELDS = ["transcription_text", "title_name", "author", "refnumber_title"]
"""Which fields should be searched by the main search field."""


class SearchView(FormView, ListView):
    template_name = "search/searchview.html"
    form_class = SearchForm
    queryset = []
    context_object_name = "results"

    def form_valid(self, form):
        self.queryset = TranscriptionDocument.search()
        if form.cleaned_data['query']:
            self.queryset = self.queryset.query("multi_match", query=form.cleaned_data['query'], fields=FULLTEXT_FIELDS)
        for filter in form.cleaned_data['filters']:
            self.queryset = filter.apply(self.queryset)
        self.queryset = self.queryset.to_queryset()
        return self.get(self.request)

    def get_context_data(self, **kwargs):
        """Add context variables."""
        context = super().get_context_data(**kwargs)
        context['ATTRIBUTES'] = Attribute.members
        return context

from django.shortcuts import render
from django.views.generic import FormView, ListView
from django_tables2 import RequestConfig

from main.documents import TranscriptionDocument
from main.forms.search_forms import SearchForm, Attribute
from main.tables import DocumentTable, DocumentResultTable

FULLTEXT_FIELDS = ["transcription_text", "title_name", "author", "ref_number_title"]

def test_search(request):
    form = SearchForm()
    table = None
    queryset = []

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            queryset = TranscriptionDocument.search()
            if form.cleaned_data['query']:
                queryset = queryset.query("multi_match", query=form.cleaned_data['query'],
                                          fields=FULLTEXT_FIELDS)
                total_count = queryset.count()
                queryset = queryset[0:total_count]

            for tr_filter in form.cleaned_data['filters']:
                print(tr_filter)
                queryset = tr_filter.apply(queryset)
            queryset = queryset.to_queryset()

            # paginator = DSEPaginator(queryset, 5)

            for q in queryset:
                print("Q:", q)

            table = DocumentResultTable(data=queryset, query=form.cleaned_data['query'])
            RequestConfig(request).configure(table)

    context = {'form': form, 'ATTRIBUTES': Attribute.members, 'results': queryset, 'table': table}
    return render(request, "main/search/search_view.html", context)


class SearchView(FormView, ListView):
    template_name = "main/search/search_view.html"
    form_class = SearchForm
    queryset = []
    context_object_name = "results"

    def form_valid(self, form):
        self.queryset = TranscriptionDocument.search()
        if form.cleaned_data['query']:
            print("QUERY: ", form.cleaned_data['query'])
            self.queryset = self.queryset.query("multi_match", query=form.cleaned_data['query'], fields=FULLTEXT_FIELDS)

        for tr_filter in form.cleaned_data['filters']:
            print(tr_filter)
            self.queryset = tr_filter.apply(self.queryset)
        self.queryset = self.queryset.to_queryset()

        return self.get(self.request)

    def get_context_data(self, **kwargs):
        """Add context variables."""
        context = super().get_context_data(**kwargs)
        context['ATTRIBUTES'] = Attribute.members
        return context

from datetime import date

from django.contrib import messages
from django.db.models import Min
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import FormView, ListView
from django_elasticsearch_dsl_drf.pagination import Paginator
from django.utils.translation import ugettext_lazy as _
from elasticsearch_dsl import Q

from main.documents import TranscriptionDocument
from main.forms.forms_search import Attribute, AdvancedSearchForm
from main.tables.tables_document import DocumentResultTable
from main.models import Document, SourceType

FULLTEXT_FIELDS = ["title_name", "transcription_text", "ref_number_title", "ref_number_name"]


def test_search_3(request):
    form = AdvancedSearchForm()
    enriched_result = None
    total_results = 0
    number_of_pages = 0
    page_size = 100
    current_page = 1
    pagination_link_list = list()

    # Form has been sent: search
    if request.method == "GET":
        form = AdvancedSearchForm(request.GET)
        if form.is_valid():
            if not form.cleaned_data['source_type'] == '' and form.cleaned_data['source_type'] is not None:
                if form.cleaned_data['source_type'].parent_type is None:
                    print("Would search for children: ", form.cleaned_data['source_type'].source_type_set.all())
                print("Source Type,,,", form.cleaned_data['source_type'], form.cleaned_data['source_type'].id)
        else:
            print("Form not valid")

        print("Search")
        search_result = TranscriptionDocument.search()
        # search_result = search_result.query("match", title_name="*brief*con*")
        #search_result = search_result.query("multi_match", query="achthunder", fields=FULLTEXT_FIELDS)
        search_result.query = Q('match', title_name='*dokument*') &\
                              (Q('match', source_type='Other Political Writings') | Q('match', source_type='Argumentative Writings') |
                               Q('match', source_type='Polemic Writings'))
        search_result.query()

        paginator = Paginator(search_result, page_size)
        result_page = paginator.page(current_page)
        enriched_result = list()
        for q in result_page:
            try:
                doc = Document.objects.get(id=q.meta.id)
                enriched_result.append([q, doc])
                # print("Q:", q, q.title_name, q.meta.id) # , q.meta.score
                """
                for hl in q.meta.highlight:
                    print("H", q.meta.highlight[hl])"""
            except Document.DoesNotExist:
                # Old versions get found by elasticsearch but are not part of the resut
                total_results -= 1

    # No form has been sent.
    else:
        pass

    context = {'form': form,  # The search form
               'form_data': get_document_filter_data(request),
               'total': total_results,  # Num of total search results
               'page_links': pagination_link_list,
               'current_page': current_page,
               'num_pages': number_of_pages,
               'result': enriched_result}  # Search result tuples: (elasticsearch-Document, Django-db-object)
    return render(request, "main/search/search_view_3.html", context)

def test_search_2(request):
    form = AdvancedSearchForm()
    enriched_result = None
    total_results = 0
    number_of_pages = 0
    page_size = 10
    current_page = 1
    pagination_link_list = list()

    if request.method == "GET":

        form = AdvancedSearchForm(request.GET)
        current_page = int(request.GET.get('page', 1))

        if form.is_valid():
            can_filter = True
            search_result = TranscriptionDocument.search()
            if not form.cleaned_data['query'] == '':
                search_result = search_result.query("multi_match", query="*"+form.cleaned_data['query'].lower()+"*", fields=FULLTEXT_FIELDS)
            # The main search field is empty
            else:
                if not form.cleaned_data['title_name'] == '':
                    search_type = "match"
                    search_term = form.cleaned_data['title_name'].lower()
                    if form.cleaned_data['title_name_exact']:
                        search_type = "match"
                        search_term = form.cleaned_data['title_name'].lower()

                    search_result = search_result.query(search_type, title_name=search_term)
                # Search AND title are empty
                else:
                    if not form.cleaned_data['ref_number_title'] == '':
                        search_type = "match"
                        search_term = "*" + form.cleaned_data['ref_number_title'].lower() + "*"
                        if form.cleaned_data['ref_number_title_exact']:
                            search_type = "match"
                            search_term = form.cleaned_data['ref_number_title'].lower()
                        search_result = search_result.query(search_type, ref_number_title=search_term)
                    # Search AND title AND ref_number_title are empty
                    else:
                        if request.GET.get('query', 'None') == '':
                            messages.warning(request, _('Please enter at least a search query or a title or a reference title.'))
                            context = {'form': form,  # The search form
                                       'total': 0,  # Num of total search results
                                       'page_links': None,
                                       'current_page': 0,
                                       'num_pages': 0,
                                       'result': None}
                            return render(request, "main/search/search_view_2.html", context)
                        can_filter = False

            # A query has been sent.
            if can_filter:
                if not form.cleaned_data['title_name'] == '':
                    search_type = "match"
                    search_term = form.cleaned_data['title_name'].lower()
                    if form.cleaned_data['title_name_exact']:
                        search_type = "match"
                        search_term = form.cleaned_data['title_name'].lower()

                    search_result = search_result.filter(search_type, title_name=search_term)
                if not form.cleaned_data['ref_number_title'] == '':
                    search_type = "match"
                    search_term = form.cleaned_data['ref_number_title'].lower()
                    if form.cleaned_data['ref_number_title_exact']:
                        search_type = "match"
                        search_term = form.cleaned_data['ref_number_title'].lower()
                    search_result = search_result.filter(search_type, ref_number_title=search_term)
                if not form.cleaned_data['ref_number_name'] == '':
                    search_type = "match"
                    search_term = form.cleaned_data['ref_number_name'].lower()
                    if form.cleaned_data['ref_number_name_exact']:
                        search_type = "match"
                        search_term = form.cleaned_data['ref_number_name'].lower()
                    search_result = search_result.filter(search_type, ref_number_name=search_term)
                if not form.cleaned_data['location'] == '':
                    search_type = "match"
                    search_term = form.cleaned_data['location']
                    if form.cleaned_data['location_exact']:
                        search_type = "match"
                        search_term = form.cleaned_data['location']
                    search_result = search_result.filter(search_type, place_name=search_term)

                if form.cleaned_data['seal']:
                    search_result = search_result.filter("match", seal=True)
                if form.cleaned_data['illuminated']:
                    search_result = search_result.filter("match", illuminated=True)

                if not form.cleaned_data['doc_start_date'] is None:
                    search_result = search_result.filter("range", doc_end_date={'gte': form.cleaned_data['doc_start_date']})
                    search_result = search_result.filter("range", doc_start_date={'lte': form.cleaned_data['doc_end_date']})

                if not form.cleaned_data['source_type'] is None:
                    search_result = search_result.filter("match", source_type=form.cleaned_data['source_type'].type_name)

            # SET Highlights
            search_result = search_result.highlight_options(order='score')
            search_result = search_result.highlight('title_name')
            search_result = search_result.highlight('ref_number_name')
            search_result = search_result.highlight('ref_number_title')
            search_result = search_result.highlight('place_name')
            search_result = search_result.highlight('transcription_text')
            search_result = search_result.highlight('source_type')
            total_results = search_result.count()
            paginator = Paginator(search_result, page_size)
            result_page = paginator.page(current_page)
            number_of_pages = paginator.num_pages

            enriched_result = list()
            for q in result_page:
                try:
                    doc = Document.objects.get(id=q.meta.id)
                    enriched_result.append([q, doc])
                    # print("Q:", q, q.title_name, q.meta.id) # , q.meta.score
                    """
                    for hl in q.meta.highlight:
                        print("H", q.meta.highlight[hl])"""
                except Document.DoesNotExist:
                    # Old versions get found by elasticsearch but are not part of the resut
                    total_results -= 1

            my_url = reverse('main:search')
            my_url += "?"
            for key in request.GET.keys():
                if key != "page":
                    my_url += key + "=" + request.GET[key] + "&"

            # print("PAGINATION BASE", my_url)
            # print("CURRENT", current_page)

            min_page = 1
            max_page = number_of_pages

            if number_of_pages > 10:
                min_page = current_page-5
                if min_page < 1:
                    min_page = 1

                max_page = current_page + 5
                if max_page > number_of_pages:
                    max_page = number_of_pages

            for pp in range(min_page, max_page+1):
                pagination_link_list.append((pp, my_url+'page='+str(pp)))
        else:
            messages.error(request, _("There are errors in your search form"))

    context = {'form': form,                # The search form
               'form_data': get_document_filter_data(request),
               'total': total_results,      # Num of total search results
               'page_links': pagination_link_list,
               'current_page': current_page,
               'num_pages': number_of_pages,
               'result': enriched_result}   # Search result tuples: (elasticsearch-Document, Django-db-object)
    return render(request, "main/search/search_view_2.html", context)


def get_document_filter_data(request):
    """Creates and returns a dict with all the data needed for the manually created
    document filter form."""

    latest_year = date.today().year
    try:
        earliest_doc = Document.objects.filter().values_list('doc_start_date').annotate(Min('doc_start_date')).order_by('doc_start_date')[0]
        earliest_year = earliest_doc[0].date.year
    except (IndexError, ValueError) as error:
        earliest_year = 1000

    form_data = {'filter_applied': 'title_name' in request.GET.keys(),
                 'min': earliest_year,
                 'max': latest_year,
                 'set_min': request.GET.get('doc_start_date', earliest_year),
                 'set_max': request.GET.get('doc_end_date', latest_year),
                 'source_types': list()}
    for st in SourceType.objects.filter(parent_type=None):
        new_line = {'name': st.get_translated_name(request.LANGUAGE_CODE),
                    'value': str(st.id),
                    'children': list()}
        for cst in SourceType.objects.filter(parent_type=st.id):
            new_line['children'].append({'name': cst.get_translated_name(request.LANGUAGE_CODE),
                                         'value': str(cst.id)})
        form_data['source_types'].append(new_line)

    return form_data

def search_box_redirect(request):
    if request.method == "POST":
        query = request.POST.get('query', '')
        if query == '':
            messages.warning(request, 'Please enter a search term')
            return redirect('main:search')
        search_url = reverse('main:search')
        search_url += "?query=" + query
        return HttpResponseRedirect(search_url)


def search_by_box_view(request, query):
    my_url = reverse('main:search')
    my_url += "?query=" + query


# TODO
def old_search_by_box_view(request, query):
    form = AdvancedSearchForm()
    queryset = TranscriptionDocument.search()
    queryset = queryset.query("multi_match", query=query,
                              fields=FULLTEXT_FIELDS)
    queryset = queryset.to_queryset()

    my_url = reverse('main:search')
    my_url += "?query="+query

    table = DocumentResultTable(data=queryset, query=query)

    context = {'form': form, 'ATTRIBUTES': Attribute.members, 'results': queryset, 'table': table}
    return render(request, "main/search/search_view.html", context)


class SearchView(FormView, ListView):
    template_name = "main/search/search_view.html"
    #form_class = SearchForm
    queryset = []
    context_object_name = "results"

    def form_valid(self, form):
        self.queryset = TranscriptionDocument.search()
        if form.cleaned_data['query']:
            # print("QUERY: ", form.cleaned_data['query'])
            self.queryset = self.queryset.query("multi_match", query=form.cleaned_data['query'], fields=FULLTEXT_FIELDS)

        for tr_filter in form.cleaned_data['filters']:
            # print(tr_filter)
            self.queryset = tr_filter.apply(self.queryset)
        self.queryset = self.queryset.to_queryset()

        return self.get(self.request)

    def get_context_data(self, **kwargs):
        """Add context variables."""
        context = super().get_context_data(**kwargs)
        context['ATTRIBUTES'] = Attribute.members
        return context

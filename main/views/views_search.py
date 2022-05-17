from datetime import date
from functools import reduce

from django.contrib import messages
from django.db.models import Min
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django_elasticsearch_dsl_drf.pagination import Paginator
from elasticsearch_dsl import Q

from main.documents import TranscriptionDocument, TranscriptionDocumentStrict
from main.forms.forms_search import AdvancedSearchForm
from main.models import Document, SourceType

FULLTEXT_FIELDS = ["title_name", "transcription_text", "ref_number_title", "ref_number_name"]


def transcriptiones_search(request):
    """View for the transcriptiones search.
    This needs two indexes: transcriptiones_idx and transcriptiones_idx_strict"""
    form = AdvancedSearchForm()
    enriched_result = None
    total_results = 0
    number_of_pages = 0
    page_size = 10
    current_page = 1
    pagination_link_list = list()
    my_url = reverse('main:search')

    # Form has been sent: search
    if request.method == "GET":
        form = AdvancedSearchForm(request.GET)
        current_page = int(request.GET.get('page', 1))
        if form.is_valid():
            strict_search = form.cleaned_data['strict_search']
            search_qs = list()
            search_result = TranscriptionDocument.search()
            if strict_search:
                search_result = TranscriptionDocumentStrict.search()

            if form.cleaned_data['query'] != '':
                search_qs.append(Q('multi_match', query=form.cleaned_data['query'], fields=FULLTEXT_FIELDS))
            # Title
            if form.cleaned_data['title_name'] != '':
                search_qs.append(Q('match', title_name=form.cleaned_data['title_name']))
            # Title
            if form.cleaned_data['ref_number_name'] != '':
                search_qs.append(Q('match', ref_number_name=form.cleaned_data['ref_number_name']))
            # Title
            if form.cleaned_data['institution_name'] != '':
                search_qs.append(Q('match', institution_name=form.cleaned_data['institution_name']))
            # Title
            if form.cleaned_data['ref_number_title'] != '':
                search_qs.append(Q('match', ref_number_title=form.cleaned_data['ref_number_title']))
            # Title
            if form.cleaned_data['location'] != '':
                search_qs.append(Q('match', place_name=form.cleaned_data['location']))
            # Title
            if form.cleaned_data['doc_start_date'] != '':
                search_qs.append(Q('range', doc_start_date={'gte': form.cleaned_data['doc_start_date']}))
            if form.cleaned_data['doc_end_date'] != '':
                search_qs.append(Q('range', doc_start_date={'lte': form.cleaned_data['doc_end_date']}))
            if form.cleaned_data['seal']:
                search_qs.append(Q("match", seal=True))
            if form.cleaned_data['illuminated']:
                search_qs.append(Q("match", illuminated=True))
            if not form.cleaned_data['source_type'] == '' and form.cleaned_data['source_type'] is not None:
                if form.cleaned_data['source_type'].parent_type is None:
                    st_list = list()
                    for s_type in SourceType.objects.filter(parent_type=form.cleaned_data['source_type']):
                        st_list.append(Q('match', source_type=s_type.type_name))

                    the_st_list = reduce(lambda x, y: x | y, st_list)
                    search_qs.append(the_st_list)
                else:
                    search_qs.append(Q('match', source_type=form.cleaned_data['source_type'].type_name))

            # Query the index
            the_bw_list = reduce(lambda x, y: x & y, search_qs)
            the_query = the_bw_list

            search_result.query = the_query
            search_result.query()

            # SET Highlights
            search_result = search_result.highlight_options(order='score')
            search_result = search_result.highlight('title_name')
            search_result = search_result.highlight('institution_name')
            search_result = search_result.highlight('ref_number_name')
            search_result = search_result.highlight('ref_number_title')
            search_result = search_result.highlight('place_name')
            search_result = search_result.highlight('transcription_text')
            search_result = search_result.highlight('source_type')

            total_results = search_result.count()
            paginator = Paginator(search_result, page_size)
            number_of_pages = paginator.num_pages
            result_page = paginator.page(current_page)

            enriched_result = list()
            for q in result_page:
                try:
                    doc = Document.objects.get(id=q.meta.id)
                    enriched_result.append([q, doc])
                except Document.DoesNotExist:
                    # Old versions get found by elasticsearch but are not part of the result
                    print("Error: retrieving one of the docs!")
                    total_results -= 1

            my_url += "?"
            for key in request.GET.keys():
                if key != "page":
                    my_url += key + "=" + request.GET[key] + "&"

            min_page = 1
            max_page = number_of_pages

            if number_of_pages > 10:
                min_page = current_page - 5
                if min_page < 1:
                    min_page = 1

                max_page = current_page + 5
                if max_page > number_of_pages:
                    max_page = number_of_pages

            for pp in range(min_page, max_page + 1):
                pagination_link_list.append((pp, my_url + 'page=' + str(pp)))
        else:
            print("Form not valid")

    # No form has been sent.
    else:
        pass

    context = {'form': form,  # The search form
               'form_data': get_document_filter_data(request),
               'total': total_results,  # Num of total search results
               'page_links': pagination_link_list,
               'first_page': my_url + 'page=1',
               'previous_page': my_url + 'page=' + str(current_page - 1),
               'current_page': current_page,
               'next_page': my_url + 'page=' + str(current_page + 1),
               'last_page': my_url + 'page=' + str(number_of_pages),
               'num_pages': number_of_pages,
               'result': enriched_result}  # Search result tuples: (elasticsearch-Document, Django-db-object)
    return render(request, "main/search/search_view_3.html", context)


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
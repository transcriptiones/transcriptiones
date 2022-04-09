from datetime import date

from django.contrib import messages
from django.db.models import Min
from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language
from django.views.generic import DetailView
from django_tables2 import MultiTableMixin, SingleTableMixin, RequestConfig
from django_filters.views import FilterView
from django.utils.translation import ugettext_lazy as _
import main.model_info as m_info
from main.models import Institution, RefNumber, Document, UserSubscription, SourceType, Author
from main.tables.tables_base import TitleValueTable
from main.tables.tables_browse import RefNumberTable, InstitutionTable, SourceTypeTable, AuthorTable
from main.tables.tables_document import DocumentTable, DocumentVersionHistoryTable, MinimalDocumentTable
from main.filters import InstitutionFilter, RefNumberFilter, DocumentFilter, AuthorFilter


def browse_options(request):
    """Shows a page with browse options: institutions, authors, Source Types. This is a static page and only
    shows the template. Can be accessed without login."""

    return render(request, 'main/details/browse_options.html')


class InstitutionListView(SingleTableMixin, FilterView):
    """Creates a list view for all institutions.
    Features a filter to filter the institution table."""

    model = Institution
    table_class = InstitutionTable
    filterset_class = InstitutionFilter
    template_name = "main/details/institution_list.html"

    def get_queryset(self):
        return Institution.objects.all().order_by('institution_name')


class AuthorListView(SingleTableMixin, FilterView):
    """Creates a list view for all source types."""

    model = Author
    table_class = AuthorTable
    filterset_class = AuthorFilter
    template_name = "main/details/author_list.html"

    def get_queryset(self):
        return Author.objects.all().order_by('author_name')


class AuthorDetailView(MultiTableMixin, DetailView):
    """View to show details of authors and list all documents of this author."""
    model = Author
    my_filter = None
    template_name = "main/details/author_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.my_filter = DocumentFilter(request.GET, Document.objects.filter(author=self.get_object()))
        return super(AuthorDetailView, self).dispatch(request, *args, **kwargs)

    def get_tables(self):
        author = self.get_object()
        data = m_info.get_author_info(author)

        tables = [
            TitleValueTable(data=data),
            DocumentTable(self.my_filter.qs)
        ]
        return tables

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.my_filter
        context['form_data'] = get_document_filter_data(self.request, self.my_filter)
        if self.request.user.is_authenticated:
            context['subscribed'] = UserSubscription.objects.filter(user=self.request.user,
                                                                    subscription_type=UserSubscription.SubscriptionType.AUTHOR,
                                                                    object_id=self.get_object().id).count() > 0
        else:
            context['subscribed'] = False
        return context


def source_type_list_view(request):
    """Creates a list view for all parent source types."""
    parent_source_type_list = SourceType.objects.filter(parent_type=None).order_by('type_name')
    context = {'source_types': parent_source_type_list}
    return render(request, "main/details/source_type_list.html", context=context)


def source_type_detail_view(request, pk):
    """Shows a view with source types. Depends if the source type to show is a parent type or a child type."""
    selected_source_type = SourceType.objects.get(id=pk)
    parent_source_type_list = SourceType.objects.filter(parent_type=None).order_by('type_name')

    if selected_source_type.parent_type is None:
        children_source_type_list = SourceType.objects.filter(parent_type=selected_source_type).order_by('type_name')
        document_list = Document.objects.filter(source_type__in=children_source_type_list)
        my_filter = DocumentFilter(request.GET, document_list)
        table = DocumentTable(data=my_filter.qs)
        RequestConfig(request).configure(table)

    else:
        document_list = Document.objects.filter(source_type=selected_source_type)
        my_filter = DocumentFilter(request.GET, document_list)
        table = MinimalDocumentTable(data=my_filter.qs)
        RequestConfig(request).configure(table)

    context = {'source_types': parent_source_type_list, 'table': table, 'selected': selected_source_type,
               'form_data': get_document_filter_data(request, my_filter)}
    return render(request, "main/details/source_type_child_detail.html", context=context)


# deprecated
def source_type_group_detail_view(request, pk):
    """Show documents of a a parent source type (e.g. The docs of all source types which have a common parent
    source type."""
    # print("PK", pk)
    selected_source_type = SourceType.objects.get(id=pk)
    parent_source_type_list = SourceType.objects.filter(parent_type=selected_source_type.parent_type).order_by('type_name')
    document_list = Document.objects.filter(source_type__in=parent_source_type_list)
    my_filter = DocumentFilter(request.GET, document_list)
    table = DocumentTable(data=my_filter.qs)
    RequestConfig(request).configure(table)
    context = {'source_types': parent_source_type_list, 'table': table, 'selected': selected_source_type, 'all': True,
               'form_data': get_document_filter_data(request, my_filter)}
    return render(request, "main/details/source_type_child_detail.html", context=context)


class InstitutionDetailView(MultiTableMixin, DetailView):
    """View to show details of institutions and list all reference numbers of this institution."""
    model = Institution
    slug_field = 'institution_slug'
    slug_url_kwarg = 'inst_slug'
    my_filter = None

    table_pagination = {
        "per_page": 20
    }
    template_name = "main/details/institution_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.my_filter = RefNumberFilter(request.GET, RefNumber.objects.filter(holding_institution=self.get_object()).order_by('ref_number_name'))
        return super(InstitutionDetailView, self).dispatch(request, *args, **kwargs)

    def get_tables(self):
        institution = self.get_object()
        data = m_info.get_institution_info(institution)

        tables = [
            TitleValueTable(data=data),
            RefNumberTable(self.my_filter.qs)
        ]
        return tables

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.my_filter
        if self.request.user.is_authenticated:
            context['subscribed'] = UserSubscription.objects.filter(user=self.request.user,
                                                                    subscription_type=UserSubscription.SubscriptionType.INSTITUTION,
                                                                    object_id=self.get_object().id).count() > 0
        else:
            context['subscribed'] = False
        return context


class RefNumberDetailView(MultiTableMixin, DetailView):
    """View to show details of institutions and list all reference numbers of this institution"""

    model = RefNumber
    slug_field = 'ref_number_slug'
    slug_url_kwarg = 'ref_slug'
    my_filter = None
    table_pagination = {
        "per_page": 20
    }

    template_name = "main/details/ref_number_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.my_filter = DocumentFilter(request.GET, Document.objects.filter(parent_ref_number=self.get_object()))
        return super(RefNumberDetailView, self).dispatch(request, *args, **kwargs)

    def get_tables(self):
        ref_number = self.get_object()
        data = m_info.get_ref_number_info(ref_number)

        tables = [
            TitleValueTable(data=data),
            DocumentTable(self.my_filter.qs),
        ]
        return tables

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.my_filter
        context['form_data'] = get_document_filter_data(self.request, self.my_filter)
        if self.request.user.is_authenticated:
            context['subscribed'] = UserSubscription.objects.filter(user=self.request.user,
                                                                    subscription_type=UserSubscription.SubscriptionType.REF_NUMBER,
                                                                    object_id=self.get_object().id).count() > 0
        else:
            context['subscribed'] = False
        return context


class DocumentDetailView(MultiTableMixin, DetailView):
    """View to display Document. Accepts optional version number to display legacy version"""
    model = Document
    slug_field = 'document_slug'
    slug_url_kwarg = 'doc_slug'

    template_name = "main/details/document_detail.html"

    def get_object(self):
        institution = self.kwargs.get('inst_slug')
        ref_number = self.kwargs.get('ref_slug')
        document = self.kwargs.get('doc_slug')
        queryset = Document.all_objects.filter(parent_ref_number__holding_institution__institution_slug=institution)
        queryset = queryset.filter(parent_ref_number__ref_number_slug=ref_number)
        queryset = queryset.filter(document_slug=document)

        # if url specifies version_number, get this specific version, else get the active version
        if 'version_nr' in self.kwargs:
            version = self.kwargs.get('version_nr')
        else:
            version = queryset.get(active=True).version_number

        try:
            result = queryset.get(document_slug=document, version_number=version)
        except Document.DoesNotExist:
            messages.error(self.request, _("The transcription version you requested is not available."))

        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # if view should display legacy version, add newest version to context
        if 'version_nr' in self.kwargs:
            newest = self.get_object().get_versions().latest()
            context['newest'] = newest

        if self.request.user.is_authenticated:
            context['subscribed'] = UserSubscription.objects.filter(user=self.request.user,
                                                                    subscription_type=UserSubscription.SubscriptionType.DOCUMENT,
                                                                    object_id=self.get_object().id).count() > 0
        else:
            context['subscribed'] = False

        return context

    def get_tables(self):
        document = self.get_object()

        tables = [
            TitleValueTable(data=m_info.get_document_info_overview(document)),
            TitleValueTable(data=m_info.get_document_info_metadata(document)),
            TitleValueTable(data=m_info.get_document_info_manuscript(document)),
            TitleValueTable(data=m_info.get_document_info_comments(document)),
        ]

        return tables


class DocumentHistoryView(MultiTableMixin, DetailView):
    """View to display version history of a DocumentTitle object"""

    model = Document
    slug_field = 'document_slug'
    slug_url_kwarg = 'doc_slug'
    my_filter = None
    table_pagination = {
        "per_page": 20
    }
    template_name = "main/details/document_history.html"

    def dispatch(self, request, *args, **kwargs):
        qs = Document.all_objects.filter(document_id=self.get_object().document_id).order_by('-document_utc_add')
        self.my_filter = DocumentFilter(request.GET, qs)
        return super(DocumentHistoryView, self).dispatch(request, *args, **kwargs)

    def get_tables(self):
        document = self.get_object()
        data = m_info.get_document_info_overview(document)

        tables = [
            TitleValueTable(data=data),
            DocumentVersionHistoryTable(self.my_filter.qs),
        ]
        return tables

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.my_filter
        context['form_data'] = get_document_filter_data(self.request, self.my_filter)
        """
        if self.request.user.is_authenticated:
            context['subscribed'] = UserSubscription.objects.filter(user=self.request.user,
                                                                    subscription_type=UserSubscription.SubscriptionType.REF_NUMBER,
                                                                    object_id=self.get_object().id).count() > 0
        else:
            context['subscribed'] = False
        """
        return context

    """
    def get_object(self):
        institution = self.kwargs.get('inst_slug')
        ref_number = self.kwargs.get('ref_slug')
        document = self.kwargs.get('doc_slug')
        queryset = Document.objects.filter(parent_ref_number__holding_institution__institution_slug=institution)
        queryset = queryset.filter(parent_ref_number__ref_number_slug=ref_number)
        return get_object_or_404(queryset, document_slug=document)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        versions = self.model.get_versions(self.get_object())
        context['versions'] = versions
        return context
    """


def get_document_filter_data(request, doc_filter):
    """Creates and returns a dict with all the data needed for the manually created
    document filter form."""

    latest_year = date.today().year
    try:
        earliest_doc = Document.objects.filter().values_list('doc_start_date').annotate(Min('doc_start_date')).order_by('doc_start_date')[0]
        earliest_year = earliest_doc[0].date.year
    except (IndexError, ValueError) as error:
        earliest_year = 1000

    form_data = {'results': doc_filter.qs.count(),
                 'filter_applied': 'title_name' in request.GET.keys(),
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


def transcription_view(request, doc_id):
    document = Document.all_objects.get(id=doc_id)
    return render(request, "main/details/transcription.html", {'document': document})

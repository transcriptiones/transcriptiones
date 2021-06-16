import django_tables2 as tables
import django.utils.html as utils
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from .models import RefNumber, Document, Institution


class TitleValueTable(tables.Table):
    """The TitleValueTable provides a simple two column table with a title and a value"""

    class Meta:
        template_name = "django_tables2/bootstrap4.html"
        attrs = {"class": "table table-sm",
                 'thead': {
                     'style': 'display: none;'}
                 }

    title = tables.Column(attrs={'td': {'style': 'text-align: left; font-weight: bold;'}})
    value = tables.Column(attrs={'td': {'style': 'text-align: left;'}})


class RefNumberTable(tables.Table):
    """The RefNumberTable shows a list of reference numbers"""

    class Meta:
        model = RefNumber
        template_name = "django_tables2/bootstrap4.html"
        fields = ("ref_number_name", "ref_number_title",)
        attrs = {"class": "table table-hover",
                 'thead': {'style': 'display: none;'},
                 'td': {'style': 'text-align: left;'}
                 }

    ref_number_name = tables.LinkColumn()
    number_of_documents = tables.Column(accessor='id')

    def render_number_of_documents(self, value, record):
        return f'{record.document_set.count()} Documents'


class InstitutionTable(tables.Table):
    """The InstitutionTable shows a list of institutions"""
    no_of_documents = tables.Column(verbose_name=_('No. of Documents'), accessor='id', orderable=False)
    no_of_ref_numbers = tables.Column(verbose_name=_('No. of Ref. Numbers'), accessor='id', orderable=False)

    class Meta:
        model = Institution
        template_name = "django_tables2/bootstrap4.html"
        fields = ("institution_name", "no_of_ref_numbers", "no_of_documents")
        attrs = {"class": "table table-hover",
                 'th': {'style': 'text-align: left;'},
                 'td': {'style': 'text-align: left;'}
                 }

    def render_no_of_documents(self, value, record):
        count = 0

        for ref_number in record.refnumber_set.all():
            count += ref_number.document_set.count()
        return utils.format_html(
            '<a href="' + record.get_absolute_url() + '">' + str(count) + ' documents</a>')

    def render_no_of_ref_numbers(self, value, record):
        return utils.format_html(
            '<a href="' + record.get_absolute_url() + '">' + str(record.refnumber_set.count()) + ' ref. numbers</a>')


class DocumentTable(tables.Table):
    """The DocumentTable shows a list of documents"""

    class Meta:
        model = Document
        template_name = "django_tables2/bootstrap4.html"
        fields = ("title_name", "place_name", "doc_start_date", "source_type", "document_utc_update")
        attrs = {"class": "table table-hover",
                 'th': {'style': 'text-align: left;'},
                 'td': {'style': 'text-align: left;'}
                 }

    title_name = tables.LinkColumn(orderable=False)
    place_name = tables.Column(orderable=False)
    doc_start_date = tables.Column(orderable=False)
    source_type = tables.Column(orderable=False)
    document_utc_update = tables.DateTimeColumn(orderable=False)


class DocumentHistoryTable(tables.Table):
    """The DocumentHistoryTable shows a list of documents"""

    class Meta:
        model = Document
        template_name = "django_tables2/bootstrap4.html"
        fields = ("title_name", "activity_type", "document_utc_add", "commit_message", "submitted_by")
        attrs = {"class": "table table-hover",
                 'th': {'style': 'text-align: left;'},
                 'td': {'style': 'text-align: left;'}
                 }

    title_name = tables.LinkColumn(orderable=False)
    activity_type = tables.Column(orderable=False, accessor='id')
    document_utc_add = tables.Column(orderable=False)
    commit_message = tables.Column(orderable=False)
    submitted_by = tables.Column(orderable=False)

    def render_activity_type(self, value, record):
        if record.version_number == 1:
            return _("Upload")
        else:
            return _("Edit")

    def render_submitted_by(self, value, record):
        if record.publish_user:
            return value
        else:
            return "Anonymous"


class DocumentResultTable(tables.Table):
    """The DocumentTable shows a list of documents"""

    def __init__(self, *args, **kwargs):
        temp = kwargs.pop("query")  # Grab from kwargs
        super(DocumentResultTable, self).__init__(*args, **kwargs)
        self.query = temp  # Assign to use later


    class Meta:
        model = Document
        template_name = "main/search_result_table.html"
        fields = ("title_name", "place_name", "doc_start_date", "source_type", "document_utc_update")
        attrs = {"class": "table double-striped",
                 'th': {'style': 'text-align: left; background: white;'},
                 'td': {'style': 'text-align: left;'}
                 }

    title_name = tables.LinkColumn(orderable=False)
    place_name = tables.Column(orderable=False)
    doc_start_date = tables.Column(orderable=False)
    source_type = tables.Column(orderable=False)
    document_utc_update = tables.DateTimeColumn(orderable=False)
    transcription_text = tables.Column()

    def render_transcription_text(self, value, record):
        import re
        found_idx = [m.start() for m in re.finditer(self.query, value)]
        print(found_idx)

        snippets = list()
        for idx in found_idx:
            start_str_idx = idx - 25
            if start_str_idx < 0:
                start_str_idx = 0
            end_str_idx = idx + 25
            if end_str_idx >= len(value):
                end_str_idx = len(value) - 1
            snippet_str = f"...{value[start_str_idx:end_str_idx]}..."
            snippet_str = snippet_str.replace(self.query, f"<b>{self.query}</b>")
            snippets.append(snippet_str)

        if len(snippets) > 0:
            value = " <b>|</b> ".join(snippets)

        value = value.replace("\n", "//")

        if len(value) > 350:
            value = value[0:350]
        return mark_safe(value)

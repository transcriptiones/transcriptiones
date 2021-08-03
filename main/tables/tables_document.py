import django_tables2 as tables
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from main.tables.tables_base import TranscriptionesTable, default_row_attrs
from main.models import Document


class DocumentTable(TranscriptionesTable):
    """The DocumentTable shows a list of documents"""

    class Meta(TranscriptionesTable.Meta):
        model = Document
        fields = ("title_name", "place_name", "doc_start_date", "source_type", "document_utc_update")
        row_attrs = default_row_attrs

    title_name = tables.Column()
    place_name = tables.Column(orderable=False)
    doc_start_date = tables.Column(orderable=False)
    source_type = tables.Column(orderable=False)
    document_utc_update = tables.DateTimeColumn(orderable=False, verbose_name=_('Last update'))

    def render_document_utc_update(self, value, record):
        if record.publish_user:
            profile_url = reverse("main:public_profile", kwargs={"username": record.submitted_by.username})
            return mark_safe(f'<small>by <a href="{profile_url}">{record.submitted_by}</a> '
                             f'at {value.strftime("%Y-%m-%d %H:%M:%S")}</small>')
        else:
            return mark_safe(f'<small>by anonymous '
                             f'at {value.strftime("%Y-%m-%d %H:%M:%S")}</small>')


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

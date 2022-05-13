"""tables_document contains table classes to display documents. There are different tables for different views"""
import django_tables2 as tables
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from django_tables2 import A

from main.tables.tables_base import TranscriptionesTable, default_row_attrs
from main.models import Document


class MinimalDocumentTable(TranscriptionesTable):
    """Minimal document table. Features the document title, its creation location and creation period
    and its last update information"""
    class Meta(TranscriptionesTable.Meta):
        model = Document
        fields = ("title_name", "place_name", "doc_start_date", "document_utc_update")
        row_attrs = default_row_attrs

    title_name = tables.LinkColumn()
    doc_start_date = tables.Column(orderable=False, verbose_name=_("Creation Period"))

    @staticmethod
    def render_document_utc_update(value, record):
        if record.publish_user:
            profile_url = reverse("main:public_profile", kwargs={"username": record.submitted_by.username})
            return mark_safe(format_lazy(_('<small>by <a href="{profile_url}">{submitted_by}</a> at {time}</small>'),
                               profile_url=profile_url, submitted_by=record.submitted_by,
                               time=value.strftime("%Y-%m-%d %H:%M:%S")))
        else:
            return mark_safe(format_lazy(_('<small>by anonymous at {time}</small>'),
                                         time=value.strftime("%Y-%m-%d %H:%M:%S")))

    @staticmethod
    def render_doc_start_date(value, record):
        ret_value = value.format('%Y', '%m/%Y', '%m/%d/%Y')
        if record.doc_end_date is not None:
            ret_value += " - " + record.doc_end_date.format('%Y', '%m/%Y', '%m/%d/%Y')
        return ret_value


class DocumentTable(MinimalDocumentTable):
    """The DocumentTable shows a list of documents"""

    class Meta(MinimalDocumentTable.Meta):
        fields = ("title_name", "place_name", "doc_start_date", "source_type", "document_utc_update")

    place_name = tables.Column(orderable=False)
    source_type = tables.Column(orderable=False)
    document_utc_update = tables.DateTimeColumn(orderable=False, verbose_name=_('Last update'))


class DocumentUserHistoryTable(TranscriptionesTable):
    """The DocumentUserHistoryTable shows a list of documents"""

    class Meta(TranscriptionesTable.Meta):
        model = Document
        fields = ("title_name", "activity_type", "document_utc_add", "commit_message")

    title_name = tables.Column(linkify=lambda record: record.get_absolute_version_url())
    activity_type = tables.Column(orderable=False, accessor='id', verbose_name=_("Action"))
    document_utc_add = tables.Column()
    commit_message = tables.Column(orderable=False)

    def render_activity_type(self, value, record):
        if record.version_number == 1:
            return _("Upload")
        else:
            return _("Edit")


class DocumentVersionHistoryTable(TranscriptionesTable):
    """The DocumentVersionHistoryTable shows a list of versions of a document"""

    class Meta(TranscriptionesTable.Meta):
        model = Document
        fields = ("version_number", "title_name", "activity_type", "document_utc_add", "commit_message", "submitted_by")

    version_number = tables.Column(verbose_name="V.")
    title_name = tables.LinkColumn('main:document_legacy_detail', args=[A('parent_ref_number__holding_institution__institution_slug'),
                                                                        A('parent_ref_number__ref_number_slug'),
                                                                        A('document_slug'),
                                                                        A('version_number')])
    activity_type = tables.Column(orderable=False, accessor='id', verbose_name=_("Action"))
    document_utc_add = tables.Column(verbose_name=_('Last Change'))
    commit_message = tables.Column(orderable=False)
    submitted_by = tables.Column(orderable=False)

    @staticmethod
    def render_activity_type(value, record):
        if record.version_number == 1:
            return _("Upload")
        else:
            return _("Edit")

    @staticmethod
    def render_submitted_by(value, record):
        if record.publish_user:
            return value
        else:
            return _('Anonymous')


class DocumentResultTable(tables.Table):
    """The DocumentTable shows a list of documents. TODO: is this used a"""

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
    # transcription_text = tables.Column()

    def render_transcription_text(self, value, record):
        import re
        found_idx = [m.start() for m in re.finditer(self.query, value)]
        # print(found_idx)

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

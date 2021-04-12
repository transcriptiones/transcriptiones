import django_tables2 as tables
from django.utils.translation import ugettext as _
from .models import RefNumber, Document


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
        fields = ("ref_number_name", "ref_number_title", )
        attrs = {"class": "table table-hover",
                 'thead': {'style': 'display: none;'},
                 'td': {'style': 'text-align: left;'}
                 }

    ref_number_name = tables.LinkColumn()
    number_of_documents = tables.Column(accessor='id')

    def render_number_of_documents(self, value, record):
        return f'{record.document_set.count()} Documents'


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

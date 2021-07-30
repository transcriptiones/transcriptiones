import django_tables2 as tables
from django.utils.safestring import mark_safe

default_table_attrs = {"class": "table table-hover table-bordered",
                       'th': {'style': 'text-align: left; padding-left: 20px;'},
                       'td': {'style': 'text-align: left; padding-left: 20px;'}
                      }

default_row_attrs = {'data-href': lambda record: record.get_absolute_url}


class TranscriptionesTable(tables.Table):

    class Meta:
        template_name = "django_tables2/bootstrap4.html"
        attrs = default_table_attrs

    def get_af_icon_label(self, before='', label_class='', after='', title=''):
        return mark_safe(f'{before}&nbsp;<i class="{label_class}" title="{title}">&nbsp;{after}</i>')


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

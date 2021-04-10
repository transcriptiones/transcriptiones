import django_tables2 as tables

from .models import RefNumber


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
        template_name = "django_tables2/bootstrap.html"
        fields = ("ref_number_name", "ref_number_title", )
        attrs = {"class": "table table-hover",
                 'thead': {'style': 'display: none;'},
                 'td': {'style': 'text-align: left;'}
                 }

    ref_number_name = tables.LinkColumn()

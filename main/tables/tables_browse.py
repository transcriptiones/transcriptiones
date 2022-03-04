"""tables_browse contains classes to display tables to browse the data (Institutions/Reference Numbers/
SourceTypes/Authors/Documents) """
import django_tables2 as tables
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from main.models import RefNumber, Institution, SourceType, Author
from main.tables.tables_base import TranscriptionesTable, default_row_attrs


class RefNumberTable(TranscriptionesTable):
    """The RefNumberTable shows a list of reference numbers"""

    ref_number_name = tables.LinkColumn()
    number_of_documents = tables.Column(accessor='id', orderable=False)

    def __init__(self, *args, **kwargs):
        self.base_columns['number_of_documents'].verbose_name = self.get_af_icon_label(before=_('No. of'),
                                                                                       label_class='far fa-file-alt',
                                                                                       title=_('Number of documents with this reference number'))
        super(RefNumberTable, self).__init__(*args, **kwargs)

    class Meta(TranscriptionesTable.Meta):
        model = RefNumber
        fields = ("ref_number_name", "ref_number_title",)

    @staticmethod
    def render_number_of_documents(value, record):
        return f'{record.document_set.count()} Documents'


class InstitutionTable(TranscriptionesTable):
    """The InstitutionTable shows a list of institutions"""

    institution_name = tables.LinkColumn()

    city = tables.Column(verbose_name=_('Location'))

    no_of_documents = tables.Column(accessor='id', orderable=False,
                                    attrs={'td': {'style': 'text-align: center;'}})

    no_of_ref_numbers = tables.Column(accessor='id', orderable=False,
                                      attrs={'td': {'style': 'text-align: center;'}})

    class Meta(TranscriptionesTable.Meta):
        model = Institution
        fields = ("institution_name", "city", "no_of_ref_numbers", "no_of_documents")
        row_attrs = default_row_attrs

    def __init__(self, *args, **kwargs):
        self.base_columns['no_of_documents'].verbose_name = self.get_af_icon_label(before=_('No. of'),
                                                                                   label_class='far fa-file-alt',
                                                                                   title=_('Number of documents in this institution'))

        self.base_columns['no_of_ref_numbers'].verbose_name = self.get_af_icon_label(before=_('No. of'),
                                                                                     label_class='far fa-folder-open',
                                                                                     title=_('Number of reference numbers in this institution'))
        super(InstitutionTable, self).__init__(*args, **kwargs)

    @staticmethod
    def render_city(value, record):
        flag = record.country.flag
        return mark_safe(value + f'&nbsp;<img src="{flag}" title="{record.country.name}">')

    @staticmethod
    def render_no_of_documents(value, record):
        count = 0
        for ref_number in record.refnumber_set.all():
            count += ref_number.document_set.count()
        return count

    @staticmethod
    def render_no_of_ref_numbers(value, record):
        return record.refnumber_set.count()


class SourceTypeTable(TranscriptionesTable):
    """The SourceTypeTable shows a list of source types"""
    type_name = tables.LinkColumn()

    no_of_documents = tables.Column(accessor='id', orderable=False)

    class Meta(TranscriptionesTable.Meta):
        model = SourceType
        fields = ("type_name", "no_of_documents")
        row_attrs = default_row_attrs

    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop("language")
        self.base_columns['no_of_documents'].verbose_name = self.get_af_icon_label(before=_('No. of'),
                                                                                   label_class='far fa-file-alt',
                                                                                   title=_(
                                                                                       'Number of documents in this institution'))
        super(SourceTypeTable, self).__init__(*args, **kwargs)

    def render_type_name(self, value, record):
        return record.get_translated_name(self.language)

    @staticmethod
    def render_no_of_documents(value, record):
        return record.document_set.count()


class AuthorTable(TranscriptionesTable):
    """The AuthorTable shows a list of authors and the number of documents and reference numbers connected to them.
    Clicking on the name shows a detail page of the author."""

    author_name = tables.LinkColumn()
    no_of_documents = tables.Column(verbose_name=_('No. of Documents'), accessor='id', orderable=False)
    no_of_ref_numbers = tables.Column(verbose_name=_('No. of Ref. Numbers'), accessor='id', orderable=False)

    class Meta(TranscriptionesTable.Meta):
        model = Author
        fields = ("author_name", "no_of_ref_numbers", "no_of_documents")
        row_attrs = default_row_attrs

    @staticmethod
    def render_no_of_documents(value, record):
        return record.document_set.count()

    @staticmethod
    def render_no_of_ref_numbers(value, record):
        ref_numbers = list()
        for doc in record.document_set.all():
            if doc.parent_ref_number not in ref_numbers:
                ref_numbers.append(doc.parent_ref_number)
        return len(ref_numbers)


class AdminAuthorTable(AuthorTable):
    pass
    # TODO AuthorTable with possibility to delete 'empty' authors
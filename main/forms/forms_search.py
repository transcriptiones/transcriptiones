"""forms_search contains all Form classes used by the transcriptiones search.
TODO it is unclear what is really used. Check this class. Also: These are not really forms"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Union, Sequence, Dict, Tuple, ClassVar, List, Type
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Button
from django import forms
from django.utils.safestring import mark_safe, SafeString
from django_elasticsearch_dsl.search import Search
from django.utils.translation import ugettext_lazy as _
from main.documents import TranscriptionDocument, ElasticsearchDocument
from main.models import Document, SourceType

DjangoFormSelectFieldOptionsList = List[Tuple[str, str]]


class Choices(Enum):
    """A specialised enum type for providing Django ChoiceField choices."""
    @classmethod
    def choices(cls) -> DjangoFormSelectFieldOptionsList:
        return [(item.name, str(item)) for item in cls]


class Operation(Choices):
    """The desired relation between the index value and the point of comparison."""
    EQUAL = ('ist',)  # Positive term query. Intended for keyword or numeric fields.
    UNEQUAL = ('ist nicht',)  # Negative term query. Intended for keyword or numeric fields.
    KEYWORD_EQUAL = ('ist',)  # Positive term query on subfield .keyword. Intended for composite fields.
    KEYWORD_UNEQUAL = ('ist nicht',)  # Negative term query on subfield .keyword. Intended for composite fields.
    CONTAINS = ('enthält',)  # Positive match query. Intended for text fields.
    CONTAINS_NOT = ('enthält nicht',)  # Negative match query. Intended for text fields.
    GTE = ('ist mindestens',)  # Upwards range query. Intended for numeric fields.
    LTE = ('ist höchstens',)  # Downwards range query. Intended for numeric fields.

    def __str__(self):
        return self.text

    def __repr__(self):
        return f'<{self.__class__.__qualname__}.{self.name}: {self}>'

    def __new__(cls, text):
        obj = object.__new__(cls)
        obj._value_ = auto()
        obj.text = text
        return obj


TEXT_OPERATIONS = (Operation.KEYWORD_EQUAL, Operation.KEYWORD_UNEQUAL, Operation.CONTAINS, Operation.CONTAINS_NOT)
NUMERIC_OPERATIONS = (Operation.EQUAL, Operation.UNEQUAL, Operation.GTE, Operation.LTE)
BINARY_OPERATIONS = (Operation.EQUAL, Operation.UNEQUAL)


class BooleanSelect(forms.NullBooleanSelect):
    """A two-element <select> for binary fields."""

    def __init__(self, attrs=None):
        choices = (
            ('true', _('Yes')),
            ('false', _('No')),
        )
        super(forms.NullBooleanSelect, self).__init__(attrs, choices)


@dataclass(frozen=True)
class Attribute:
    """The potential filter criteria.

    During import, this caches some information, namely possible choice values that may depend on index population
    at import time. They can be refreshed at any time by calling Attribute.build_members()
    """
    name: str
    field: str
    operations: Sequence[Operation] = TEXT_OPERATIONS
    widget: forms.Widget = forms.TextInput()

    members: ClassVar[Dict[str, Attribute]] = {}
    """All attributes, mapped from their field names to the Attribute object. Filled after class creation."""

    def __str__(self):
        return self.name

    def __class_getitem__(cls, item):
        return cls.members[item]

    def __iter__(self):
        return iter(self.members)

    @property
    def template_name(self) -> str:
        return f"{self.field}-template"

    @property
    def template(self) -> SafeString:
        """Renders the associated widget as HTML. Intended for copying."""
        return self.widget.render(self.template_name, "", {'id': self.template_name, 'class': 'value_field'})

    @staticmethod
    def _choices_for_document_field(field: str, document: Type[ElasticsearchDocument] = TranscriptionDocument,
                                    **filters) -> DjangoFormSelectFieldOptionsList:
        """Find all distinct entries of a field (capped to 10 000), in a format for Django's choice fields

        Any further keyword arguments are used to filter by a match query.
        """
        s = document.search()[:0]
        if filters:
            s = s.query('match', **filters)
        s.aggs.bucket('choices', 'terms', field=field, size=10_000)
        results = s.execute()
        choices_list = sorted(
            [bucket['key'] for bucket in results.aggregations.choices.buckets]
        )
        return [(choice, choice) for choice in choices_list]

    @classmethod
    def build_members(cls):
        """Populates Attribute.members. Call once after class creation, and again for clearing the option cache."""
        cls.members = {str(a): a for a in [
            cls("Text", 'transcription_text', (Operation.CONTAINS, Operation.CONTAINS_NOT)),
            cls("Institut", 'institution_name'),
            cls("Signatur", 'refnumber_title'),
            cls("Titel", 'title_name'),
            cls("Sprache", 'language', BINARY_OPERATIONS,
                forms.Select(choices=cls._choices_for_document_field('language'))),
            cls("Quellgattung", 'source_type', BINARY_OPERATIONS,
                forms.Select(choices=cls._choices_for_document_field('source_type'))),
            cls("Jahr", 'year', NUMERIC_OPERATIONS, forms.NumberInput({'step': '1', 'style': 'width: 4em'})),
            cls("Datum", 'date', NUMERIC_OPERATIONS, forms.DateInput({'type': 'date'})),
            cls("Seitenzahl", 'pages', NUMERIC_OPERATIONS, forms.NumberInput({'step': '1', 'min': '0'})),
            cls("Seitenlänge", 'measurements_length', NUMERIC_OPERATIONS,
                forms.NumberInput({'step': '0.1', 'min': '0'})),
            cls("Seitenbreite", 'measurements_width', NUMERIC_OPERATIONS,
                forms.NumberInput({'step': '0.1', 'min': '0'})),
            cls("Illuminiert", 'illuminated', BINARY_OPERATIONS, BooleanSelect()),
            cls("Siegel", 'seal', BINARY_OPERATIONS, BooleanSelect()),
            cls("Material", 'material', BINARY_OPERATIONS,
                forms.Select(choices=Document.MaterialType.choices)),
            cls("Paginierung", 'paging_system', BINARY_OPERATIONS,
                forms.Select(choices=Document.PaginationType.choices)),
            cls("Startdatum", 'doc_start_date', NUMERIC_OPERATIONS, forms.NumberInput({'step': '1', 'min': '0'})),
            cls("Endatum", 'doc_end_date', NUMERIC_OPERATIONS, forms.NumberInput({'step': '1', 'min': '0'}))
        ]}


Attribute.build_members()


@dataclass(frozen=True)
class FilterTriple:
    """A filter condition."""
    attribute: Attribute
    operation: Operation
    value: object

    def as_dict(self):
        return {self.attribute.field: self.value}

    def as_dict_with_kw(self):
        return {f'{self.attribute.field}.keyword': self.value}

    def apply(self, search: Search) -> Search:
        """Restrict an ElasticSearch search by this filter."""
        if self.operation is Operation.EQUAL:
            return search.filter('term', **self.as_dict())
        if self.operation is Operation.UNEQUAL:
            return search.exclude('term', **self.as_dict())
        if self.operation is Operation.KEYWORD_EQUAL:
            return search.filter('term', **self.as_dict_with_kw())
        if self.operation is Operation.KEYWORD_UNEQUAL:
            return search.exclude('term', **self.as_dict_with_kw())
        if self.operation is Operation.CONTAINS:
            return search.filter('match', **self.as_dict())
        if self.operation is Operation.GTE:
            return search.filter('range', **{self.attribute.field: {'gte': self.value}})
        if self.operation is Operation.LTE:
            return search.filter('range', **{self.attribute.field: {'lte': self.value}})
        raise ValueError(self.operation)

    def __repr__(self):
        return f'<FilterTriple: {self.attribute} {self.operation} {self.value!r}>'


class AttributeSelect(forms.Select):
    """A specialised <select> widget for an Attribute."""
    def create_option(self, name, value: str, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            attribute = Attribute[value]
            option['attrs']['data-operations'] = ','.join(op.name for op in attribute.operations)
            option['attrs']['data-template-name'] = attribute.template_name
        return option


class FilterWidget(forms.MultiWidget):
    """A tripartite widget to enter a filter."""
    def __init__(self, attrs=None, divattrs: dict = None):
        """
        :param attrs: Applied to all subwidgets.
        :param divattrs: If this is not None, the subwidgets are enclosed with a div element with the attributes
                         specified in it.
        """
        if attrs is None:
            attrs = {}
        widgets = [  # TODO: Change to dict for better field names once Django 3.1 is released.
            AttributeSelect(attrs=_append_class(attrs, 'attribute_field'), choices=[(a, a) for a in Attribute.members]),
            forms.Select(attrs=_append_class(attrs, 'operation_field'), choices=Operation.choices()),
            forms.TextInput(attrs=_append_class(attrs, 'value_field')),
        ]
        super().__init__(widgets, attrs)
        self.divattrs = divattrs

    def render(self, name, value, attrs=None, renderer=None):
        inner_html = super().render(name, value, attrs, renderer)
        inner_html += '<button type="button" class="btn btn-danger removal_button">&times;</button>'
        if self.divattrs is not None:
            divattrs = _append_class(self.divattrs, 'filter_field')
            divattr_str = ' '.join(f'{key}="{value}"' for (key, value) in divattrs.items())
            return mark_safe(f'<div {divattr_str}>{inner_html}</div>')
        else:
            return inner_html

    def decompress(self, value: Optional[FilterTriple]) -> Union[Tuple[Attribute, Operation, object],
                                                                 Tuple[None, None, None]]:
        if value is None:
            return None, None, None
        return Attribute[value.attribute], Operation[value.operation], value.value


def _append_class(attrs: dict, class_name: str):
    attrs = attrs.copy()
    if 'class' in attrs:
        attrs['class'] += f' {class_name}'
    else:
        attrs['class'] = class_name
    return attrs


class FilterField(forms.MultiValueField):
    def __init__(self, **kwargs):
        fields = (
            forms.ChoiceField(choices=[(a, a) for a in Attribute.members]),
            forms.ChoiceField(choices=Operation.choices()),
            forms.CharField(),
        )
        super().__init__(fields, widget=kwargs.pop('widget', FilterWidget), **kwargs)

    def compress(self, data_list) -> Optional[FilterTriple]:
        attribute, operation, value = data_list
        if not value:
            return None
        return FilterTriple(Attribute[attribute], Operation[operation], value)


class AdvancedSearchForm(forms.Form):
    """Search form. This class is not used to render the form but the validation functionality is used. Because of the
    ui specifications of the form, the actual render is a template (main/search/search_form.html) which included in the search view"""
    query = forms.CharField(required=False, label=_('Full Text Search'), help_text=_('Search within the title and contents of documents.'))
    title_name = forms.CharField(required=False, label=_('Document Title'))
    institution_name = forms.CharField(required=False, label=_('Institution Name'))
    ref_number_title = forms.CharField(required=False, label=_('Reference Title'))
    ref_number_name = forms.CharField(required=False, label=_('Reference Name'))
    source_type = forms.ModelChoiceField(required=False, queryset=SourceType.objects.all())
    location = forms.CharField(required=False, label=_('Location'))
    seal = forms.BooleanField(required=False, label=_('Document must have seal'))
    illuminated = forms.BooleanField(required=False, label=_('Document must have illuminations'))
    strict_search = forms.BooleanField(required=False, label='Activate Strict Search') # Dummy

    title_name_exact = forms.BooleanField(required=False)
    ref_number_title_exact = forms.BooleanField(required=False)
    ref_number_name_exact = forms.BooleanField(required=False)
    location_exact = forms.BooleanField(required=False)

    doc_start_date = forms.IntegerField(required=False, label=_('Published Earliest Year'))
    doc_end_date = forms.IntegerField(required=False, label=_('Published Latest Year'))
    #manuscript_pages = forms.IntegerField(required=False, label=_('Minimum No. of Pages'))

    def __init__(self, *args, **kwargs):
        """The layout configuration is useless as it is not used."""
        super(AdvancedSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'query',
            Row(
                Column('title_name', css_class='form-group col-md-5 mb-0'),
                Column('title_name_exact', css_class='form-group col-md-1 mb-0'),
                Column('ref_number_title', css_class='form-group col-md-5 mb-0'),
                Column('ref_number_title_exact', css_class='form-group col-md-1 mb-0'),
                Column('ref_number_name', css_class='form-group col-md-5 mb-0'),
                Column('ref_number_name_exact', css_class='form-group col-md-1 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('source_type', css_class='form-group col-md-6 mb-0'),
                Column('location', css_class='form-group col-md-5 mb-0'),
                Column('location_exact', css_class='form-group col-md-1 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('year_from', css_class='form-group col-md-4 mb-0'),
                Column('year_to', css_class='form-group col-md-4 mb-0'),
                # Column('manuscript_pages', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('seal', css_class='form-group col-md-6 mb-0'),
                Column('illuminated', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', _('Search'), css_class='btn-primary'),
            Button('clear', 'Clear Form', css_class='btn-secondary', onclick='window.location.href="{}"'.format('/search'))
        )
        self.helper.form_method = 'GET'

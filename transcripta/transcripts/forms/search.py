from dataclasses import dataclass, astuple
from enum import Enum
from typing import Optional, Type, Sequence

from django import forms
from django.forms.widgets import Input as InputWidget
from django.utils.safestring import mark_safe


class Choices(Enum):
    """A specialised enum type for providing Django ChoiceField choices."""
    @classmethod
    def choices(cls):
        return [(item.name, item.value) for item in cls]


class Operation(Choices):
    """The desired relation between the index value and the point of comparison."""
    EQUAL = 'ist'
    UNEQUAL = 'ist nicht'
    CONTAINS = 'enthält'


KEYWORD_OPERATIONS = (Operation.EQUAL, Operation.UNEQUAL, Operation.CONTAINS)


@dataclass(frozen=True)
class Attribute:
    """The potential filter criteria.

    These are implemented manually and therefore do not have to correspond to model fields.
    """
    name: str
    operations: Sequence[Operation] = KEYWORD_OPERATIONS
    widget: Type[InputWidget] = forms.TextInput

    def __str__(self):
        return self.name

    @property
    def input_type(self):
        return self.widget.input_type


ATTRIBUTES = [
    Attribute("Institut"),
    Attribute("Signatur"),
]


@dataclass(frozen=True)
class FilterTriple:
    """A filter condition."""
    attribute: Attribute
    operation: Operation
    value: object


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
            forms.Select(attrs=_append_class(attrs, 'attribute_field'), choices=[(a, a.name) for a in ATTRIBUTES]),
            forms.Select(attrs=_append_class(attrs, 'operation_field'), choices=Operation.choices()),
            forms.TextInput(attrs=_append_class(attrs, 'value_field')),
        ]
        super().__init__(widgets, attrs)
        self.divattrs = divattrs

    def render(self, name, value, attrs=None, renderer=None):
        inner_html = super().render(name, value, attrs, renderer)
        if self.divattrs is not None:
            divattrs = _append_class(self.divattrs, 'filter_field')
            divattr_str = ' '.join(f'{key}="{value}"' for (key, value) in divattrs.items())
            return mark_safe(f'<div {divattr_str}>{inner_html}</div>')
        else:
            return inner_html

    def decompress(self, value: Optional[FilterTriple]) -> tuple:
        if value is None:
            return None, None, None
        return astuple(value)


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
            forms.ChoiceField(choices=[(a, a.name) for a in ATTRIBUTES]),
            forms.ChoiceField(choices=Operation.choices()),
            forms.CharField(),
        )
        super().__init__(fields, widget=kwargs.pop('widget', FilterWidget), **kwargs)

    def compress(self, data_list) -> Optional[FilterTriple]:
        attribute, operation, value = data_list
        if not value:
            return None
        return FilterTriple(attribute, Operation[operation], value)


class SearchForm(forms.Form):
    query = forms.CharField(label=False, widget=forms.widgets.TextInput(attrs={'type': 'search'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 11):
            filter_field = FilterField(label=False, required=False)
            if i == 1:
                filter_field.widget.divattrs = {}
            else:
                filter_field.widget.divattrs = {'class': 'd-none'}
            self.fields[f'filter_{i}'] = filter_field

    def clean(self):
        filters = []
        filter_names = [name for name in self.cleaned_data.keys() if name.startswith('filter_')]
        for filter_name in filter_names:
            filter = self.cleaned_data.pop(filter_name, None)
            if filter is None or not filter.value:
                continue
            filters.append(filter)
        self.cleaned_data['filters'] = filters

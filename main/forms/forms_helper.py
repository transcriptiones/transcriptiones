"""forms_helper contains helper functions to initialize the transcriptiones forms"""
from django.utils import six
from crispy_forms.helper import FormHelper
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.text import format_lazy

from main import model_info

mark_safe_lazy = lazy(mark_safe, six.text_type)


def initialize_form_helper():
    """Creates a FormHelper object and defines the table classes to create the form fields."""
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-3'
    helper.field_class = 'col-sm-9'
    return helper


def get_popover_html(model, field_name, content=None):
    """Returns a form label, enhanced with a html tooltip. """
    label = model._meta.get_field(field_name).verbose_name
    tooltip = model_info.get_extended_help_text(model, field_name) if content is None else content
    ret_value = format_lazy('{label}&nbsp;<span data-toggle="tooltip" data-html="true" data-placement="top" title="{tooltip}"><i class="fas fa-info-circle"></i></span>',
                            label=_(label), tooltip=tooltip)

    # ret_value = _(label) + f'&nbsp;<span data-toggle="tooltip" data-html="true" data-placement="top" title="{tooltip}">' \
    #                        f'<i class="fas fa-info-circle"></i>' \
    #                        f'</span>'
    return mark_safe_lazy(ret_value)

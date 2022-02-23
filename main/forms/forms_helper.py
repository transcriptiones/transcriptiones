from django.utils import six
from crispy_forms.helper import FormHelper
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from main import model_info

mark_safe_lazy = lazy(mark_safe, six.text_type)


def initialize_form_helper():
    """Creates a FormHelper object and defines the table classes to create the form fields."""
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-3'
    helper.field_class = 'col-sm-9'
    return helper


"""def get_popover_html(model, field_name, content=None):
    label = model._meta.get_field(field_name).verbose_name
    tooltip = model_info.get_extended_help_text(model, field_name) if content is None else content
    ret_value = _(label) + f' <i class="fas fa-info-circle tooltipster" data-tooltip-content="#tt_{field_name}"></i>\
                        <div class="tooltip_templates"><div id="tt_{field_name}">\
                        <p>{tooltip}</p>\
                        </div></div>'
    # TODO: Test mark safe lazy
    return mark_safe_lazy(ret_value)"""


def get_popover_html(model, field_name, content=None):
    label = model._meta.get_field(field_name).verbose_name
    tooltip = model_info.get_extended_help_text(model, field_name) if content is None else content
    ret_value = _(label) + f'&nbsp;<span class="badge badge-secondary" type="button" data-toggle="tooltip" data-html="true" data-placement="top" title="{tooltip}">?</span>'
    return mark_safe_lazy(ret_value)

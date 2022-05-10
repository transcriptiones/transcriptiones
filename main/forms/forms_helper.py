"""forms_helper contains helper functions to initialize the transcriptiones forms"""
from django.core.exceptions import FieldDoesNotExist
from django.utils import six
from crispy_forms.helper import FormHelper
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _

from main import model_info
from main.models import Document, RefNumber

mark_safe_lazy = lazy(mark_safe, six.text_type)


def initialize_form_helper(option=None):
    """Creates a FormHelper object and defines the table classes to create the form fields."""
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-3'
    helper.field_class = 'col-sm-9'
    if option == "modal_popup":
        helper.label_class = 'col-sm-4'
        helper.field_class = 'col-sm-8'
    return helper


def get_popover_html(model, field_name, content=None):
    """Returns a form label, enhanced with a html tooltip. """
    try:
        label = model._meta.get_field(field_name).verbose_name
    except FieldDoesNotExist:
        label = field_name

        if field_name == "parent_institution":
            label = _("Institution")
        elif field_name == "selection_helper_source_type":
            label = _("Parent Source Type")
        elif field_name == "password1":
            label = _('Password')
        elif field_name == 'password2':
            label = _('Confirm Password')
        elif field_name == "new_password1":
            label = _('New Password')
        elif field_name == 'new_password2':
            label = _('Confirm New Password')
        elif field_name == 'old_password':
            label = _('Old password')

    tooltip = model_info.get_extended_help_text(model, field_name) if content is None else content
    ret_value = format_lazy('{label}&nbsp;<span data-toggle="tooltip" data-html="true" data-placement="top" '\
                            'title="{tooltip}"><i class="fas fa-info-circle"></i></span>', label=label, tooltip=tooltip)
    return mark_safe_lazy(ret_value)


def get_popover_html_by_model_name(model_name, field_name):
    if model_name.lower() == "document":
        return get_popover_html(Document, field_name)
    return "no model found"


def get_help_text_html_by_model_name(model_name, field_name):
    text = "No help_text found"
    if model_name.lower() == "document":
        if field_name == "parent_institution":
            text = RefNumber._meta.get_field("holding_institution").help_text
        if field_name == "parent_ref_number":
            text = Document._meta.get_field("parent_ref_number").help_text
        if field_name == "source_type":
            text = _("Child source type")
        if field_name == "selection_helper_source_type":
            text = _("Parent source type")
        if field_name == "author":
            text = Document._meta.get_field("author").help_text
        if field_name == "language":
            text = Document._meta.get_field("language").help_text
    return mark_safe(f'<small id="hint_id_{field_name}" class="form-text text-muted">{text}</small>')
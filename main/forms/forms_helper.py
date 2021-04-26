from crispy_forms.helper import FormHelper
from main import model_info


def initialize_form_helper():
    """Creates a FormHelper object and defines the table classes to create the form fields."""
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-3'
    helper.field_class = 'col-sm-9'
    return helper


def get_popover_html(model, field_name, content=None):
    label = model._meta.get_field(field_name).verbose_name

    tooltip = model_info.get_extended_help_text(model, field_name) if content is None else content
    return label + f' <i class="fas fa-info-circle tooltipster" data-tooltip-content="#tt_{field_name}"></i>\
                     <div class="tooltip_templates"><div id="tt_{field_name}">\
                        <p>{tooltip}</p>\
                     </div></div>'

from django import template
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from django.template.base import FilterExpression

from main.forms.forms_helper import get_popover_html_by_model_name, get_help_text_html_by_model_name

register = template.Library()

@register.filter
def safe_em_only(text):
    first_index_1 = text.find("<")
    first_index_2 = text.find(">")
    if first_index_2 < first_index_1:
        text = text[first_index_2+1:]

    temp_text = text.replace("<em>", "SOMETHING_WHICH_IS_NEVER_FOUND_START")
    temp_text = temp_text.replace("</em>", "SOMETHING_WHICH_IS_NEVER_FOUND_STOP")
    temp_text = strip_tags(temp_text)
    temp_text = temp_text.replace("SOMETHING_WHICH_IS_NEVER_FOUND_START", "<em>")
    temp_text = temp_text.replace("SOMETHING_WHICH_IS_NEVER_FOUND_STOP", "</em>")
    return temp_text


@register.simple_tag
def get_static_tooltip_html(title, text):
    tooltip = format_lazy('<b>{title}</b><br/>{text}', title=title, text=text)
    return mark_safe(f'&nbsp;<span data-toggle="tooltip" data-html="true" data-placement="top" title="{tooltip}">' \
                            f'<i class="fas fa-info-circle"></i>' \
                            f'</span>')

@register.simple_tag
def get_tooltip_html(model_name, field_name):
    return get_popover_html_by_model_name(model_name, field_name)

@register.simple_tag
def get_help_text_html(model_name, field_name):
    return get_help_text_html_by_model_name(model_name, field_name)

@register.simple_tag
def get_translated_source_type_name(source_type, language):
    return source_type.get_translated_name(language)

@register.simple_tag
def get_translated_source_type_description(source_type, language):
    return source_type.get_translated_description(language)

@register.tag
def collapsed_card(parser, token):
    return create_card(parser, token, collapsed=True, end_tag="endcollapsedcard")


@register.tag
def card(parser, token):
    return create_card(parser, token)


def create_card(parser, token, collapsed=False, end_tag="endcard"):
    """This tag creates a bootstrap card node"""
    try:
        tag_name, card_id, card_title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r takes two arguments: the card id and title" % token.contents.split()[0])

    nodelist = parser.parse((end_tag,))
    parser.delete_first_token()

    card_id = FilterExpression(card_id, parser)
    card_title = FilterExpression(card_title, parser)

    return CardNode(card_id, card_title, nodelist, collapsed)


class CardNode(template.Node):
    def __init__(self, card_id, card_title, nodelist, collapsed):
        self.card_id = card_id
        self.card_title = card_title
        self.nodelist = nodelist
        self.collapsed = collapsed

    def render(self, context):
        card_id = self.card_id.resolve(context) if self.card_id else 'generic_card_id'
        card_title = self.card_title.resolve(context) if self.card_title else 'Set a Title'

        show_class = ""
        if not self.collapsed:
            show_class = " show"

        output = \
            '<div class="card mt-3 shadow">' \
            f'  <div class="card-header small text-right" data-toggle="collapse" data-target="#{card_id}">' \
            f'    <a class="card-link">{_(card_title)} </a>' \
            '  </div>' \
            f'  <div id="{card_id}" class="collapse{show_class}">' \
            '    <div class="card-body">' \
            '      <div class="row">' \
            '        <div class="col-sm text-left">' \
            f'         {self.nodelist.render(context)}' \
            '        </div>' \
            '      </div>' \
            '    </div>' \
            '  </div>' \
            '</div>'
        return output
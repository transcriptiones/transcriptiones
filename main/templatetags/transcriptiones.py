from django import template
from django.utils.translation import ugettext as _
from django.template.base import FilterExpression
register = template.Library()


@register.tag
def card(parser, token):
    """This tag creates a bootstrap card node"""
    try:
        tag_name, card_id, card_title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r takes two arguments: the card id and title" % token.contents.split()[0])

    nodelist = parser.parse(('endcard',))
    parser.delete_first_token()

    card_id = FilterExpression(card_id, parser)
    card_title = FilterExpression(card_title, parser)

    return CardNode(card_id, card_title, nodelist)


class CardNode(template.Node):
    def __init__(self, card_id, card_title, nodelist):
        self.card_id = card_id
        self.card_title = card_title
        self.nodelist = nodelist

    def render(self, context):
        card_id = self.card_id.resolve(context) if self.card_id else 'generic_card_id'
        card_title = self.card_title.resolve(context) if self.card_title else 'Set a Title'

        output = \
            '<div class="card">' \
            f'  <div class="card-header" data-toggle="collapse" href="#{card_id}">' \
            f'    <a class="card-link">{_(card_title)} </a>' \
            '  </div>' \
            f'  <div id="{card_id}" class="collapse show">' \
            '    <div class="card-body">' \
            f'      {self.nodelist.render(context)}' \
            '    </div>' \
            '  </div>' \
            '</div>'
        return output


@register.inclusion_tag('text_card.html')
def text_card(title, text):
    """Provides a bootstrap Card to display static text."""
    return {'title': title, 'text': text}


@register.simple_tag
def get_verbose_name(transcriptiones_object, field_name):
    """Provides the possibility to get the (translated) verbose name of a model object. """
    return transcriptiones_object._meta.get_field(field_name).verbose_name

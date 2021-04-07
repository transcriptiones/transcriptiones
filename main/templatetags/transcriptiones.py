from django.template.loader_tags import register


@register.inclusion_tag('text_card.html')
def text_card(title, text):
    return {'title': title, 'text': text}

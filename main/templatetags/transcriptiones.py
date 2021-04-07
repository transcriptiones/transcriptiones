from django.template.loader_tags import register


@register.inclusion_tag('text_card.html')
def text_card(title, text):
    """Provides a bootstrap Card to display static text."""
    return {'title': title, 'text': text}


@register.simple_tag
def get_verbose_name(transcriptiones_object, field_name):
    """Provides the possibility to get the (translated) verbose name of a model object. """
    return transcriptiones_object._meta.get_field(field_name).verbose_name

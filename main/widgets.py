from django.forms.widgets import Select


class SourceChildSelect(Select):
    """Widget that passes information about parent as data-attribute to every option"""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value:
            child = self.choices.queryset.get(pk=value)
            option['attrs']['data-parent'] = child.parent_type.pk
        return option

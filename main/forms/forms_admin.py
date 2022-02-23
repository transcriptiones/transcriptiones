from django.utils.translation import ugettext_lazy as _
from crispy_forms.layout import Submit
from django import forms
from main.forms.forms_helper import initialize_form_helper


class ContactMessageReplyForm(forms.Form):
    """Form to edit user message notification policy."""

    def __init__(self, *args, **kwargs):
        super(ContactMessageReplyForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('cancel', _('Cancel'), css_class='btn-secondary', formnovalidate='formnovalidate'))
        self.helper.add_input(Submit('submit', _('Send Answer'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

    subject = forms.CharField(label=_('Subject'))
    answer = forms.CharField(widget=forms.Textarea)

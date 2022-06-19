"""forms_admin contains all Form classes used by transcriptiones admin. """
from django.utils.translation import ugettext_lazy as _
from crispy_forms.layout import Submit
from django import forms
from main.forms.forms_helper import initialize_form_helper
from main.models import Newsletter


class ContactMessageReplyForm(forms.Form):
    """Form to reply to a contact message sent by an unregistered person (by email-address) or a
    registered user (when requesting a batch upload)"""

    def __init__(self, *args, **kwargs):
        super(ContactMessageReplyForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('cancel', _('Cancel'), css_class='btn-secondary', formnovalidate='formnovalidate'))
        self.helper.add_input(Submit('submit', _('Send Answer'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

    subject = forms.CharField(label=_('Subject'))
    answer = forms.CharField(widget=forms.Textarea)


class SendNewsletterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SendNewsletterForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('cancel', _('Cancel'), css_class='btn-secondary', formnovalidate='formnovalidate'))
        self.helper.add_input(Submit('submit', _('Send Test Newsletter'), css_class='btn-primary'))
        self.helper.add_input(Submit('submit', _('Send Newsletter'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

    class Meta:
        model = Newsletter
        exclude = ('creation_time', )

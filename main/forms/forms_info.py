from django.utils.translation import ugettext as _
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,\
    PasswordChangeForm, PasswordResetForm, SetPasswordForm

from main.models import User, UserMessage
from main.forms.forms_helper import initialize_form_helper, get_popover_html


class ContactForm(forms.Form):
    """Form to edit user message notification policy."""

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Send Message'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

    subject = forms.CharField()
    reply_to = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
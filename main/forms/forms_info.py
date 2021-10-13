from django.utils.translation import ugettext_lazy as _
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

    subject = forms.CharField(label=_('Subject'), initial='Question about transcriptiones.ch',
                              help_text='Change the subject to something more meaningful, if possible.')
    reply_to = forms.EmailField(label=_('Reply E-Mail'), help_text=_("We are going to reply to this E-Mail address."))
    message = forms.CharField(widget=forms.Textarea, help_text=_('Please be as specific as you can in your message. '
                                                                 'It will help us to answer your questions!'))

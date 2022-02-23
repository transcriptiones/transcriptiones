from django.utils.translation import ugettext_lazy as _
from crispy_forms.layout import Submit, Layout, Row, Column, Field
from django import forms
from main.forms.forms_helper import initialize_form_helper


class NewsletterSubscribeForm(forms.Form):
    email_address = forms.EmailField(label=_('Subscribe To Newsletter'))

    def __init__(self, *args, **kwargs):
        super(NewsletterSubscribeForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Row(
                Column('email_address', css_class='form-group col-md-10 mb-0'),
                Column(Submit('submit', _('Subscribe')), css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
        )


class NewsletterUnsubscribeForm(forms.Form):
    email_address = forms.EmailField(label=_('Unsubscribe From Newsletter'))

    def __init__(self, *args, **kwargs):
        super(NewsletterUnsubscribeForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Row(
                Column('email_address', css_class='form-group col-md-10 mb-0'),
                Column(Submit('submit', _('Unsubscribe')), css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
        )


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



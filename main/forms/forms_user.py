from django.utils.translation import ugettext_lazy as _
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,\
    PasswordChangeForm, PasswordResetForm, SetPasswordForm

from main.models import User, UserMessage
from main.forms.forms_helper import initialize_form_helper


class WriteMessageForm(forms.ModelForm):
    """Form to edit user message notification policy."""

    def __init__(self, *args, **kwargs):
        rec_user = kwargs.pop('user', None)
        subject = kwargs.pop('subject', None)
        message = kwargs.pop('message', None)

        super(WriteMessageForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Send Message'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

        if rec_user:
            self.fields['receiving_user'].initial = rec_user
        if subject:
            self.fields['subject'].initial = subject
        if message:
            self.fields['message'].initial = message

        self.fields['receiving_user'].disabled = True

    class Meta:
        model = UserMessage
        fields = ('receiving_user', 'subject', 'message')


class UserMessageOptionsForm(forms.ModelForm):
    """TODO Needs to be looked at"""
    def __init__(self, *args, **kwargs):
        super(UserMessageOptionsForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

    """Form to edit user message notification policy."""
    class Meta:
        model = User
        fields = ('message_notification_policy', )


class UserSubscriptionOptionsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserSubscriptionOptionsForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

    """Form to edit user notification policy."""
    class Meta:
        model = User
        fields = ('notification_policy', 'different_editor_subscription')


class SignUpForm(UserCreationForm):
    """Form to sign up for transcriptiones"""

    email = forms.EmailField(label=_('E-Mail'), max_length=255,
                             help_text=_('E-Mail-Address. We will send an activation Link to this address.'))
    # mark_anonymous = forms.BooleanField(label='Anonym publizieren', required=False)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        """
        for name in self.fields.keys():
            if isinstance(self.fields[name], forms.BooleanField):
                self.fields[name].widget.attrs.update({'class': 'form-check-input'})
            else:
                self.fields[name].widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': self.fields[name].help_text,
                    })
            if name.startswith('password'):
                self.fields[name].widget.attrs.update({
                    'placeholder': self.fields[name].label
                    })"""
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Register'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'ui_language', 'email', 'password1', 'password2')
        """
        labels = {
            'username': get_popover_html(User, 'username'),
            'first_name': get_popover_html(User, 'first_name'),
            'last_name': get_popover_html(User, 'last_name'),
            'email': get_popover_html(User, 'email'),
            'mark_anonymous': get_popover_html(User, 'mark_anonymous')
        }"""


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                })
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Login'), css_class='btn-primary'))
        self.helper.form_method = 'POST'


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[name].label,
                })

        self.helper = initialize_form_helper()


class UserUpdateForm(forms.ModelForm):
    # pass class form-control to form fields
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        """for name in self.fields.keys():
            if isinstance(self.fields[name], forms.BooleanField):
                self.fields[name].widget.attrs.update({'class': 'form-check-input'})
            else:
                self.fields[name].widget.attrs.update({
                    'class': 'form-control',
                    })"""

        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Save Changes'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

    username = forms.CharField(disabled=True, help_text=_('You cannot change your username'))
    email = forms.EmailField(disabled=True, help_text=_('You cannot change your email address'))
    user_orcid = forms.CharField(required=False,)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_orcid', 'mark_anonymous')


class CustomPasswordResetForm(PasswordResetForm):
    # pass class form-control to form fields
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                })
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Reset Password'), css_class='btn-primary'))
        self.helper.form_method = 'POST'


class CustomSetPasswordForm(SetPasswordForm):
    # pass class form-control to form fields
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[name].label,
                })
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Reset Password'), css_class='btn-primary'))
        self.helper.form_method = 'POST'


class RequestUsernameForm(forms.Form):
    email_of_user = forms.EmailField(label=_('Your E-Mail Address'), required=True,
                                     help_text=_('Please enter the e-mail address you registered with. '
                                                 'We will send you an e-mail with your username.'))

    def __init__(self, *args, **kwargs):
        super(RequestUsernameForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Request Username'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

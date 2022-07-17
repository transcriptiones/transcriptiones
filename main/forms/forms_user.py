"""forms_user contains Form classes to write user messages and to set the users preferences"""
import re

from captcha.fields import CaptchaField
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from crispy_forms.layout import Submit, Field
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,\
    PasswordChangeForm, PasswordResetForm, SetPasswordForm

from main.models import User, UserMessage
from main.forms.forms_helper import initialize_form_helper, get_popover_html


class WriteMessageForm(forms.ModelForm):
    """Form to write a message to another user."""

    captcha = CaptchaField()

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
    """Form to edit user message notification policy."""

    def __init__(self, *args, **kwargs):
        super(UserMessageOptionsForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

    class Meta:
        model = User
        fields = ('message_notification_policy', )


class UserSubscriptionOptionsForm(forms.ModelForm):
    """Form to edit user notification policy."""

    def __init__(self, *args, **kwargs):
        super(UserSubscriptionOptionsForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

    class Meta:
        model = User
        fields = ('notification_policy', 'different_editor_subscription')


class SignUpForm(UserCreationForm):
    """Form to sign up for transcriptiones"""

    email = forms.EmailField(label=get_popover_html(User, 'email'), max_length=255,
                             help_text=_('Email address. We will send an activation link to this address.'))

    password1 = forms.CharField(
        label=get_popover_html(User, 'password1'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_('Choose your transcriptiones password.'),
    )

    password2 = forms.CharField(
        label=get_popover_html(User, 'password2'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_('Enter the same password as before, for verification.'),
    )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Register'), css_class='btn-primary'))
        self.helper.form_method = 'POST'
        tos_url = reverse('main:tos')
        self.fields['tos_accepted'] = forms.BooleanField(
            label=_('Accept Terms of Service'),
            required=True,
            help_text=mark_safe(_('In order to sign up you are required to accept the %s and agree that '
                                  'all uploaded transcriptions will be will be subject to a %s.') %
                                  (_(f'<a href="{tos_url}" target="_blank" rel="noopener noreferrer">terms and conditions</a>'),
                                   _('<a href="https://creativecommons.org/share-your-work/public-domain/cc0/" target="_blank" rel="noopener noreferrer">CC0 licence</a>'))))

    def clean_user_orcid(self):
        data = self.cleaned_data['user_orcid']
        # Orcid can be empty
        if data == '':
            return data
        # If it is not, it must have the correct form
        if not bool(re.match("^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}$", data)):
            raise ValidationError("Your ORCID must be a valid 4 number block: 1234-1234-1234-1234")
        return data

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'user_orcid', 'ui_language', 'email', 'password1', 'password2')

        labels = {
            'username': get_popover_html(User, 'username'),
            'first_name': get_popover_html(User, 'first_name'),
            'last_name': get_popover_html(User, 'last_name'),
            'user_orcid': get_popover_html(User, 'user_orcid'),
            'mark_anonymous': get_popover_html(User, 'mark_anonymous'),
            'ui_language': get_popover_html(User, 'ui_language'),
        }


class LoginForm(AuthenticationForm):
    """Login form for transcriptiones users"""

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Login'), css_class='btn-primary'))
        self.helper.form_method = 'POST'


class CustomPasswordChangeForm(PasswordChangeForm):
    """Form to change a user's password"""
    old_password = forms.CharField(
        label=get_popover_html(User, 'old_password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True}),
        help_text=_('Enter your old transcriptiones password.')
    )

    new_password1 = forms.CharField(
        label=get_popover_html(User, 'new_password1'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_('Set a new password for transcriptiones.'),
    )

    new_password2 = forms.CharField(
        label=get_popover_html(User, 'new_password2'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_('Enter the same password as before, for verification.'),
    )

    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()


class UserUpdateForm(forms.ModelForm):
    """Form to update user information"""
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Save Changes'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

    username = forms.CharField(disabled=True, help_text=_('You cannot change your username'), label=get_popover_html(User, 'username'))
    email = forms.EmailField(disabled=True, help_text=_('You can change your email address in the respective form'), label=get_popover_html(User, 'email')) # TODO: Include url to email change form

    def clean_user_orcid(self):
        data = self.cleaned_data['user_orcid']
        # Orcid can be empty
        if data == '':
            return data
        # If it is not, it must have the correct form
        if not bool(re.match("^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}$", data)):
            raise ValidationError("Your ORCID must be a valid 4 number block: 1234-1234-1234-1234")
        return data

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_orcid', 'ui_language', 'mark_anonymous')

        labels = {
            'first_name': get_popover_html(User, 'first_name'),
            'last_name': get_popover_html(User, 'last_name'),
            'user_orcid': get_popover_html(User, 'user_orcid'),
            'ui_language':get_popover_html(User, 'ui_language'),
            'mark_anonymous': get_popover_html(User, 'mark_anonymous'),
        }


class CustomPasswordResetForm(PasswordResetForm):
    """Form to reset a users password"""
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Reset Password'), css_class='btn-primary'))
        self.helper.form_method = 'POST'


class CustomSetPasswordForm(SetPasswordForm):

    new_password1 = forms.CharField(
        label=get_popover_html(User, 'new_password1'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_('Set a new password for transcriptiones.'),
    )

    new_password2 = forms.CharField(
        label=get_popover_html(User, 'new_password2'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_('Enter the same password as before, for verification.'),
    )

    """Form to set a password"""
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Reset Password'), css_class='btn-primary'))
        self.helper.form_method = 'POST'


class RequestUsernameForm(forms.Form):
    """Form to request a user's username by entering his email address"""
    email_of_user = forms.EmailField(label=_('Your Email Address'), required=True,
                                     help_text=_('Please enter the email address you registered with. '
                                                 'We will send you an email with your username.'))

    def __init__(self, *args, **kwargs):
        super(RequestUsernameForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Request Username'), css_class='btn-primary'))
        self.helper.form_method = 'POST'


class ChangeEmailForm(forms.Form):
    """Form to request a user's username by entering his email address"""
    new_email_of_user = forms.EmailField(label=_('Your New Email Address'), required=True,
                                         help_text=_('Please enter the email address you want to use for transcriptiones.'))

    def __init__(self, *args, **kwargs):
        super(ChangeEmailForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Change Address'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

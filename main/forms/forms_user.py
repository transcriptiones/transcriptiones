from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,\
    PasswordChangeForm, PasswordResetForm, SetPasswordForm

from main.models import User
from main.forms.forms_helper import initialize_form_helper, get_popover_html


class SignUpForm(UserCreationForm):
    """Form to sign up for transcriptiones"""

    email = forms.EmailField(label='E-Mail', max_length=255, help_text='E-Mail-Adresse')
    mark_anonymous = forms.BooleanField(label='Anonym publizieren', required=False)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
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
                    })
        self.helper = initialize_form_helper()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'mark_anonymous')
        labels = {
            'username': get_popover_html(User, 'username'),
            'first_name': get_popover_html(User, 'first_name'),
            'last_name': get_popover_html(User, 'last_name'),
            'email': get_popover_html(User, 'email'),
            'mark_anonymous': get_popover_html(User, 'mark_anonymous')
        }


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                })


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
        for name in self.fields.keys():
            if isinstance(self.fields[name], forms.BooleanField):
                self.fields[name].widget.attrs.update({'class': 'form-check-input'})
            else:
                self.fields[name].widget.attrs.update({
                    'class': 'form-control',
                    })

        self.helper = initialize_form_helper()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'mark_anonymous')


class CustomPasswordResetForm(PasswordResetForm):
    # pass class form-control to form fields
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                })


class CustomSetPasswordForm(SetPasswordForm):
    # pass class form-control to form fields
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[name].label,
                })

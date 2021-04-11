from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UserChangeForm, PasswordResetForm, SetPasswordForm
from main.models import User


class SignUpForm(UserCreationForm):
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

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'mark_anonymous')


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


class UserUpdateForm(forms.ModelForm):
    # form field to prompt for password
    passwordprompt = forms.CharField(
        label="Passwort",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Zur Bestätigung Passwort eingeben'}),
    )

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

    # check password. Raise ValidationError if password invalid
    def clean_passwordprompt(self):
        valid = self.instance.check_password(self.cleaned_data['passwordprompt'])
        if not valid:
            raise forms.ValidationError("Falsches Passwort")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'mark_anonymous', 'passwordprompt')


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

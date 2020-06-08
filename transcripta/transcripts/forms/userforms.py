from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UserChangeForm, PasswordResetForm, SetPasswordForm
from transcripta.transcripts.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=255, help_text='E-Mail-Adresse')
    anonymous_publication = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                })

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'anonymous_publication')

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
                })

class UserUpdateForm(forms.ModelForm):
    # form field to prompt for password
    passwordprompt = forms.CharField(
        label="Geben Sie Ihr Passwort ein, um die Änderungen zu bestätigen.",
        strip=False,
        widget=forms.PasswordInput(),
    )

    # pass class form-control to form fields
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
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
        fields = ('username', 'email', 'anonymous_publication', 'passwordprompt')

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
                })
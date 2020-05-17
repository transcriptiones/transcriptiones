from django import forms
from django.contrib.auth.forms import UserCreationForm
from transcripta.transcripts.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=255, help_text='Email-Adresse')
    anonymous_publication = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                })

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'anonymous_publication')

from django import forms
from main.forms.forms_helper import initialize_form_helper
from main.models import Document


class EditTranscriptionForm(forms.ModelForm):
    """This is the edit form for the transcription part of a document."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

    class Meta:
        model = Document
        fields = ('transcription_text', 'commit_message')


class EditMetaForm(forms.ModelForm):
    """This is the edit form for the meta part of a document."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

    class Meta:
        model = Document
        fields = ('transcription_text', )
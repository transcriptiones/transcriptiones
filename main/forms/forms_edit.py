from dal import autocomplete
from django import forms
from main.forms.forms_helper import initialize_form_helper
from main.models import Document, Author, Language, SourceType
from django.utils.translation import ugettext_lazy as _


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

    selection_helper_source_type = forms.ModelChoiceField(
                                        label=_('First level Source Type'),
                                        queryset=SourceType.objects.filter(parent_type=None).order_by('type_name'),
                                        widget=autocomplete.ModelSelect2(url='main:srctype-autocomplete'))

    source_type = forms.ModelChoiceField(queryset=SourceType.objects.exclude(parent_type=None).order_by('type_name'),
                                         widget=autocomplete.ModelSelect2(url='main:srctype-ch-autocomplete',
                                                                          forward=['selection_helper_source_type', ]))


    author = forms.ModelMultipleChoiceField(queryset=Author.objects.all().order_by('author_name'),
                                            widget=autocomplete.ModelSelect2Multiple(url='main:author-autocomplete'),
                                            required=False)

    language = forms.ModelMultipleChoiceField(queryset=Language.objects.all().order_by('name_native'),
                                              widget=autocomplete.ModelSelect2Multiple(
                                                  url='main:language-autocomplete'),
                                              required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

    class Meta:
        model = Document
        exclude = ('title_name', 'parent_ref_number', 'transcription_text', 'institution_utc_add',
                   'document_slug', 'version_number')

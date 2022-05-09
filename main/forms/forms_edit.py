"""forms_admin contains all Form classes used to edit documents. There are separate forms to
edit the meta data and the transcription itself"""
from dal import autocomplete
from django import forms
from main.forms.forms_helper import initialize_form_helper, get_popover_html
from main.models import Document, Author, Language, SourceType
from django.utils.translation import ugettext_lazy as _


class EditTranscriptionForm(forms.ModelForm):
    """This is the edit form for the transcription part of a document."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

    class Meta:
        model = Document
        fields = ('transcription_text', 'commit_message', 'publish_user')

        labels = {
            'commit_message': get_popover_html(Document, 'commit_message'),
            'publish_user': get_popover_html(Document, 'publish_user'),
        }


class EditMetaForm(forms.ModelForm):
    """This is the edit form for the meta part of a document."""

    selection_helper_source_type = forms.ModelChoiceField(
                                        label=_('First level Source Type'),
                                        queryset=SourceType.objects.filter(parent_type=None).order_by('type_name'),
                                        widget=autocomplete.ModelSelect2(url='main:srctype-autocomplete',
                                                                         attrs={'data-html': True}))

    source_type = forms.ModelChoiceField(queryset=SourceType.objects.exclude(parent_type=None).order_by('type_name'),
                                         widget=autocomplete.ModelSelect2(url='main:srctype-ch-autocomplete',
                                                                          forward=['selection_helper_source_type', ],
                                                                          attrs={'data-html': True}))

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

        labels = {
            'transcription_scope': get_popover_html(Document, 'transcription_scope'),
            'doc_start_date': get_popover_html(Document, 'doc_start_date'),
            'doc_end_date': get_popover_html(Document, 'doc_end_date'),
            'place_name': get_popover_html(Document, 'place_name'),
            'transcription_text': get_popover_html(Document, 'transcription_text'),
            'material': get_popover_html(Document, 'material'),
            'measurements_width': get_popover_html(Document, 'measurements_width'),
            'measurements_length': get_popover_html(Document, 'measurements_length'),
            'pages': get_popover_html(Document, 'pages'),
            'paging_system': get_popover_html(Document, 'paging_system'),
            'illuminated': get_popover_html(Document, 'illuminated'),
            'seal': get_popover_html(Document, 'seal'),
            'commit_message': get_popover_html(Document, 'commit_message'),
            'publish_user': get_popover_html(Document, 'publish_user'),
        }
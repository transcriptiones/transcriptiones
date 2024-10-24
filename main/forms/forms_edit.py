"""forms_admin contains all Form classes used to edit documents. There are separate forms to
edit the meta data and the transcription itself"""
from dal import autocomplete
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy

from main.forms.forms_helper import initialize_form_helper, get_popover_html, get_clean_partial_date
from main.models import Document, Author, Language, SourceType
from django.utils.translation import ugettext_lazy as _


class EditTranscriptionForm(forms.ModelForm):
    """This is the edit form for the transcription part of a document."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        tos_url = reverse('main:tos')
        self.fields['accept_tos'] = forms.BooleanField(
            label=_('Accept Terms of Service'),
            required=True,
            help_text=mark_safe(
                _('In order to commit your changes you are required to accept the %s and agree that '
                  'all uploaded transcriptions will be will be subject to a %s.') %
                (format_lazy('<a href="{tos_url}" target="_blank" rel="noopener noreferrer">{tos_text}</a>', tos_url=tos_url, tos_text=_('terms of service')),
                 _('<a href="https://creativecommons.org/share-your-work/public-domain/cc0/" target="_blank" rel="noopener noreferrer">CC0 licence</a>'))))

    class Meta:
        model = Document
        fields = ('transcription_text', 'transcription_scope', 'commit_message', 'publish_user')

        labels = {
            'transcription_scope': get_popover_html(Document, 'transcription_scope'),
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
                                            required=True)

    language = forms.ModelMultipleChoiceField(queryset=Language.objects.all().order_by('name_native'),
                                              widget=autocomplete.ModelSelect2Multiple(
                                                  url='main:language-autocomplete'),
                                              required=True)

    seal = forms.NullBooleanField(label=get_popover_html(Document, 'seal'),
                                  help_text=Document._meta.get_field("seal").help_text,
                                  widget=forms.Select(
                                      choices=[('', _('(Unknown)')), (True, _('Yes')), (False, _('No'))]),
                                  required=False)

    illuminated = forms.NullBooleanField(label=get_popover_html(Document, 'illuminated'),
                                         help_text=Document._meta.get_field("illuminated").help_text,
                                         widget=forms.Select(
                                             choices=[('', _('(Unknown)')), (True, _('Yes')), (False, _('No'))]),
                                         required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        tos_url = reverse('main:tos')
        self.fields['accept_tos'] = forms.BooleanField(
            label=_('Accept Terms of Service'),
            required=True,
            help_text=mark_safe(
                _('In order to commit your changes you are required to accept the %s and agree that '
                  'all uploaded transcriptions will be will be subject to a %s.') %
                (format_lazy('<a href="{tos_url}" target="_blank" rel="noopener noreferrer">{tos_text}</a>', tos_url=tos_url, tos_text=_('terms of service')),
                 _('<a href="https://creativecommons.org/share-your-work/public-domain/cc0/" target="_blank" rel="noopener noreferrer">CC0 licence</a>'))))

    def clean_doc_start_date(self):
        data = self.cleaned_data['doc_start_date']
        new_data = get_clean_partial_date(data)
        return new_data

    def clean_doc_end_date(self):
        data = self.cleaned_data['doc_end_date']
        new_data = get_clean_partial_date(data)
        return new_data

    class Meta:
        model = Document
        exclude = ('title_name', 'parent_ref_number', 'transcription_text', 'institution_utc_add',
                   'document_slug', 'version_number', 'transcription_scope')

        labels = {
            'doc_start_date': get_popover_html(Document, 'doc_start_date'),
            'doc_end_date': get_popover_html(Document, 'doc_end_date'),
            'place_name': get_popover_html(Document, 'place_name'),
            'transcription_text': get_popover_html(Document, 'transcription_text'),
            'material': get_popover_html(Document, 'material'),
            'measurements_width': get_popover_html(Document, 'measurements_width'),
            'measurements_length': get_popover_html(Document, 'measurements_length'),
            'pages': get_popover_html(Document, 'pages'),
            'paging_system': get_popover_html(Document, 'paging_system'),
            # 'illuminated': get_popover_html(Document, 'illuminated'),
            # 'seal': get_popover_html(Document, 'seal'),
            'comments': get_popover_html(Document, 'comments'),
            'commit_message': get_popover_html(Document, 'commit_message'),
            'publish_user': get_popover_html(Document, 'publish_user'),
        }
import re

from captcha.fields import ReCaptchaField
from crispy_forms.layout import Submit
from django import forms
from bootstrap_modal_forms.forms import BSModalModelForm
from dal import autocomplete
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy

from django.utils.translation import ugettext_lazy as _

from main.models import Institution, RefNumber, Document, SourceType, Author, Language
from main.widgets import SourceChildSelect
from main.forms.forms_helper import initialize_form_helper, get_popover_html, get_clean_partial_date, \
    get_help_text_html_by_model_name


class LanguageModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """Form field for Language objects which renders the label to display the english and native name"""

    def label_from_instance(self, obj):
        return f'{obj.name_en} ({obj.name_native})'


class UploadTranscriptionForm(forms.ModelForm):
    """This is the upload form to upload a new transcribed document."""
    parent_institution = forms.ModelChoiceField(queryset=Institution.objects.all().order_by('institution_name'),
                                                widget=autocomplete.ModelSelect2(url='main:inst-autocomplete'))

    parent_ref_number = forms.ModelChoiceField(queryset=RefNumber.objects.all().order_by('ref_number_name'),
                                               widget=autocomplete.ModelSelect2(url='main:refn-autocomplete',
                                                                                forward=['parent_institution', ]))

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

    language = LanguageModelMultipleChoiceField(queryset=Language.objects.all().order_by('name_native'),
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

    # TODO illuminated = forms.NullBooleanField(widget=forms.Select(choices=((True, _('Yes')), (),)))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        field = 'title_name'
        #print(field, objprint(self.fields[field]), type(self.fields[field]))
        """if self.fields[field].widget.is_required:
            self.fields[field].label = "my_css_class_for_required_fields"
        """
        tos_url = reverse('main:tos')
        self.fields['accept_tos'] = forms.BooleanField(
            label=_('Accept Terms of Service'),
            required=True,
            help_text=mark_safe(_('In order to upload your transcription you are required to accept the %s and agree that '
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
        exclude = ('institution_utc_add', 'document_slug', 'version_number', 'commit_message')

        labels = {
            'title_name': get_popover_html(Document, 'title_name'),
            # 'parent_institution': no crispy field
            # 'parent_ref_number': no crispy field
            'transcription_scope': get_popover_html(Document, 'transcription_scope'),
            'doc_start_date': get_popover_html(Document, 'doc_start_date'),
            'doc_end_date': get_popover_html(Document, 'doc_end_date'),
            'place_name': get_popover_html(Document, 'place_name'),
            # 'selection_helper_source_type': no crispy field
            # 'source_type': no crispy field
            'transcription_text': get_popover_html(Document, 'transcription_text'),
            # 'author': no crispy field
            # 'language': no crispy field
            'material': get_popover_html(Document, 'material'),
            'measurements_width': get_popover_html(Document, 'measurements_width'),
            'measurements_length': get_popover_html(Document, 'measurements_length'),
            'pages': get_popover_html(Document, 'pages'),
            'paging_system': get_popover_html(Document, 'paging_system'),
            # 'illuminated': get_popover_html(Document, 'illuminated'),
            # 'seal': get_popover_html(Document, 'seal'),
            'comments': get_popover_html(Document, 'comments'),
            'publish_user': get_popover_html(Document, 'publish_user'),
        }


class RefnModelForm(BSModalModelForm):
    """TODO """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self['holding_institution'].initial.ref_url_required:
            self.fields['collection_link'].required = True
        self.helper = initialize_form_helper(option="modal_popup")
        self.helper.add_input(Submit('submit', _('Create'), css_class='btn-secondary'))

    holding_institution = forms.ModelChoiceField(queryset=Institution.objects.order_by('institution_name'),
                                                 disabled=True, label=get_popover_html(RefNumber, 'holding_institution'))

    class Meta:
        model = RefNumber
        fields = [
            'holding_institution',
            'ref_number_name',
            'ref_number_title',
            'collection_link']

        labels = {
            'ref_number_name': get_popover_html(RefNumber, 'ref_number_name'),
            'ref_number_title': get_popover_html(RefNumber, 'ref_number_title'),
            'collection_link': get_popover_html(RefNumber, 'collection_link'),
        }


class InstModelForm(BSModalModelForm):
    """TODO """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = initialize_form_helper(option="modal_popup")
        self.helper.add_input(Submit('submit', _('Create'), css_class='btn-secondary'))

    class Meta:
        model = Institution
        fields = [
            'institution_name',
            'street',
            'zip_code',
            'city',
            'country',
            'site_url']

        labels = {
            'institution_name': get_popover_html(Institution, 'institution_name'),
            'street': get_popover_html(Institution, 'street'),
            'zip_code': get_popover_html(Institution, 'zip_code'),
            'city': get_popover_html(Institution, 'city'),
            'country': get_popover_html(Institution, 'country'),
            'site_url': get_popover_html(Institution, 'site_url')
        }


class EditMetaForm(forms.ModelForm):
    """Form for editing Metadata"""
    source_type_parent = forms.ModelChoiceField(
        queryset=SourceType.objects.filter(parent_type__isnull=True).order_by('type_name'),
        required=True,
        help_text='Ebene 1',
        label='Archivalienart',
        )
    source_type_child = forms.ModelChoiceField(
        queryset=SourceType.objects.filter(parent_type__isnull=False).order_by('type_name'),
        required=False,
        help_text='Ebene 2',
        widget=SourceChildSelect,
        )

    seal = forms.BooleanField()
    illuminated = forms.BooleanField()

    # pass .form-control to form fields
    def __init__(self, *args, **kwargs):
        super(EditMetaForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            if isinstance(self.fields[name], forms.BooleanField):
                self.fields[name].widget.attrs.update({'class': 'form-check-input'})
            else:
                self.fields[name].widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': self.fields[name].help_text,
                    })

        self.helper = initialize_form_helper()
    
    class Meta:
        model = Document
        fields = ['author',
                  'doc_start_date',
                  'doc_end_date',
                  'place_name',
                  'language',
                  'source_type_parent',
                  'source_type_child',
                  'material',
                  'measurements_length',
                  'measurements_width',
                  'pages',
                  'paging_system',
                  'illuminated',
                  'seal',
                  'comments',
                  'commit_message',
                  # TODO 'submitted_by_anonymous',
                  ]


class EditTranscriptForm(forms.ModelForm):
    """Form to edit the transcript"""
    # pass .form-control to form fields
    def __init__(self, *args, **kwargs):
        super(EditTranscriptForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        """Override save to prevent m2m-fields from being cleared
        Get the unsaved DocumentTitle instance and their m2m-relations"""
        instance = forms.ModelForm.save(self, False)
        authors = instance.author.all()
        languages = instance.language.all()

        # Prepare a 'save_m2m' method for the form,
        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            # link the document with their m2m-relations
            instance.author.clear()
            instance.author.add(*list(authors))
            instance.language.clear()
            instance.language.add(*list(languages))

        self.save_m2m = save_m2m

        # Do we need to save all changes now?
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        model = Document
        fields = ['transcription_scope',
                  'transcription_text',
                  'commit_message',
                  # TODO 'submitted_by_anonymous',
                  ]


class BatchUploadForm(forms.Form):
    batch_title = forms.CharField(label=_('Message Title'),
                                  help_text=_('What kind of documents do you want to upload?'))
    batch_description = forms.CharField(label=_('Batch Description'),
                                        help_text=_('Please describe the documents you want to upload. Be as specific as possible'),
                                        widget=forms.Textarea)
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super(BatchUploadForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Send Message'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

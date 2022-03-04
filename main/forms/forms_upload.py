from crispy_forms.layout import Submit
from django import forms
from bootstrap_modal_forms.forms import BSModalModelForm
from dal import autocomplete

from django.utils.translation import ugettext_lazy as _

from main.models import Institution, RefNumber, Document, SourceType, Author, Language
from main.widgets import SourceChildSelect
from main.forms.forms_helper import initialize_form_helper, get_popover_html


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
                                        widget=autocomplete.ModelSelect2(url='main:srctype-autocomplete'))

    source_type = forms.ModelChoiceField(queryset=SourceType.objects.exclude(parent_type=None).order_by('type_name'),
                                         widget=autocomplete.ModelSelect2(url='main:srctype-ch-autocomplete',
                                                                          forward=['selection_helper_source_type', ]))

    author = forms.ModelMultipleChoiceField(queryset=Author.objects.all().order_by('author_name'),
                                            widget=autocomplete.ModelSelect2Multiple(url='main:author-autocomplete'),
                                            required=False)

    language = LanguageModelMultipleChoiceField(queryset=Language.objects.all().order_by('name_native'),
                                                widget=autocomplete.ModelSelect2Multiple(
                                                    url='main:language-autocomplete'),
                                                required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

    class Meta:
        model = Document
        exclude = ('institution_utc_add', 'document_slug', 'version_number', 'commit_message')

        labels = {
            'title_name': get_popover_html(Document, 'title_name'),
            'parent_institution': 'todo',
            'parent_ref_number': get_popover_html(Document, 'parent_ref_number'),
            'author': get_popover_html(Document, 'author'),
            'place_name': get_popover_html(Document, 'place_name'),
            'language': get_popover_html(Document, 'language'),
            'material': get_popover_html(Document, 'material'),
            'pages': get_popover_html(Document, 'pages'),
            'paging_system': get_popover_html(Document, 'paging_system'),
            'illuminated': get_popover_html(Document, 'illuminated'),
            'seal': get_popover_html(Document, 'seal'),
            'transcription_scope': get_popover_html(Document, 'transcription_scope'),
            'comments': get_popover_html(Document, 'comments'),
            'transcription_text': get_popover_html(Document, 'transcription_text'),
            'publish_user': get_popover_html(Document, 'publish_user'),
        }


class InstitutionForm(BSModalModelForm):
    """Form for adding an Institution which is not yet in the Database"""

    # Add class form-control to each form field for bootstrap integration
    def __init__(self, *args, **kwargs):
        super(InstitutionForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

    class Meta:
        model = Institution
        fields = [
            'institution_name',
            'street',
            'zip_code',
            'city',
            'country',
            'site_url',
            'institution_slug']

        labels = {
            'institution_name': get_popover_html(Institution, 'institution_name'),
            'street': get_popover_html(Institution, 'street'),
            'city': get_popover_html(Institution, 'city'),
            'country': get_popover_html(Institution, 'country'),
            'site_url': get_popover_html(Institution, 'site_url')
        }


class RefNumberForm(forms.ModelForm):
    """Form for adding a RefNumber which is not yet in the Database"""

    # Add class form-control to each form input for bootstrap integration
    def __init__(self, *args, **kwargs):
        super(RefNumberForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

    class Meta:
        model = RefNumber
        fields = [
            'holding_institution',
            'ref_number_name',
            'ref_number_title',
            'collection_link']

        labels = {
            'holding_institution': get_popover_html(RefNumber, 'holding_institution'),
            'ref_number_name': get_popover_html(RefNumber, 'ref_number_name'),
            'ref_number_title': get_popover_html(RefNumber, 'ref_number_title'),
            'collection_link': get_popover_html(RefNumber, 'collection_link'),
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

    def __init__(self, *args, **kwargs):
        super(BatchUploadForm, self).__init__(*args, **kwargs)
        self.helper = initialize_form_helper()
        self.helper.add_input(Submit('submit', _('Send Message'), css_class='btn-primary'))
        self.helper.form_method = 'POST'

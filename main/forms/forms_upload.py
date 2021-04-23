from ckeditor.widgets import CKEditorWidget
from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import ugettext as _
from main.models import Institution, RefNumber, Document, SourceType
from main.widgets import SourceChildSelect


class InstitutionForm(forms.ModelForm):
    """Form for adding an Institution which is not yet in the Database"""

    # Add class form-control to each form field for bootstrap integration
    def __init__(self, *args, **kwargs):
        super(InstitutionForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[name].help_text,
                })
        
        self.fields['zip_code'].widget.attrs.update({
            'max': 99999
            })

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-9'

    class Meta:
        model = Institution
        fields = ['institution_name', 'street', 'zip_code', 'city', 'country', 'site_url', 'institution_slug']


class RefNumberForm(forms.ModelForm):
    """Form for adding a RefNumber which is not yet in the Database"""

    # Add class form-control to each form input for bootstrap integration
    def __init__(self, *args, **kwargs):
        super(RefNumberForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[name].help_text,
                })

    class Meta:
        model = RefNumber
        fields = ['holding_institution', 'ref_number_name', 'ref_number_title', 'collection_link']


def popover_html(field_name, content=None):
    label = Document._meta.get_field(field_name).verbose_name
    tooltip = Document._meta.get_field(field_name).help_text if content is None else content
    return label + f' <i class="fas fa-info-circle tooltipster" data-tooltip-content="#tt_{field_name}"></i>\
                     <div class="tooltip_templates"><div id="tt_{field_name}">\
                        <p>{tooltip}</p>\
                     </div></div>'


class DocumentForm(forms.ModelForm):
    """Form for adding a new Document to the Database"""

    class Meta:
        model = Document
        fields = ['title_name',
                  'parent_institution',
                  'parent_ref_number',
                  'author',
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
                  # TODO 'illuminated',
                  # TODO 'seal',
                  'transcription_scope',
                  'comments',
                  'transcription_text',
                  'document_slug',
                  'publish_user',
                  ]

        labels = {
            'title_name': popover_html('title_name'),
            'parent_institution': popover_html('parent_institution', _('')),
            'parent_ref_number': popover_html('parent_ref_number', _('')),
            'author': popover_html('author', _('')),
            'place_name': popover_html('place_name', _('')),
            'language': popover_html('language', _('')),
            'material': popover_html('material', _('')),
            'pages': popover_html('pages', _('')),
            'paging_system': popover_html('paging_system', _('')),
            'transcription_scope': popover_html('transcription_scope', _('')),
            'comments': popover_html('comments', _('')),
            'transcription_text': popover_html('transcription_text', _('')),
            'publish_user': popover_html('publish_user', _('')),
        }

    transcription_text = forms.CharField(widget=CKEditorWidget)
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
        # TODO widget=SourceChildSelect,
        )

    # add class form-control to each form input for bootstrap integration
    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            if isinstance(self.fields[name], forms.BooleanField):
                self.fields[name].widget.attrs.update({'class': 'form-check-input'})
            else:
                self.fields[name].widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': self.fields[name].help_text,
                    })

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-9'


        """ TODO check This. Bit it probably isnt needed anymore
        self.fields['start_year'].widget.attrs.update({
            'min': -3000, # ToDo: Probably solve this with validators? Do the same for end_dates
            'max': datetime.now().year
            })
        """

        # handle dependent dropdowns
        self.fields['parent_ref_number'].queryset = RefNumber.objects.none()

        if 'parent_institution' in self.data:
            try:
                institution_id = int(self.data.get('parent_institution'))
                self.fields['parent_ref_number'].queryset = RefNumber.objects.filter(holding_institution_id=institution_id).order_by('ref_number_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['parent_ref_number'].queryset = self.instance.holding_institution.refnumber_set.order_by('ref_number_name')


# Form for editing Metadata
class EditMetaForm(forms.ModelForm):
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

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-9'
    
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
    
    # pass .form-control to form fields
    def __init__(self, *args, **kwargs):
        super(EditTranscriptForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            if isinstance(self.fields[name], forms.BooleanField):
                self.fields[name].widget.attrs.update({'class': 'form-check-input'})
            else:
                self.fields[name].widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': self.fields[name].help_text,
                    })

    # Override save to prevent m2m-fields from being cleared
    def save(self, commit=True):
        # Get the unsaved DocumentTitle instance and their m2m-relations
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
from datetime import datetime
from django import forms

from transcripta.transcripts.models import Institution, RefNumber, DocumentTitle, SourceType
from transcripta.transcripts.widgets import SourceChildSelect


#Form for adding an Institution which is not yet in the Database
class InstitutionForm(forms.ModelForm):
    #add class form-control to each form field for bootstrap integration
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

    class Meta:
        model = Institution
        fields = ['institution_name', 'street', 'zip_code', 'city', 'country', 'site_url', 'institution_slug']


#Form for adding a RefNumber which is not yet in the Database
class RefNumberForm(forms.ModelForm):
    
    #add class form-control to each form input for bootstrap integration
    def __init__(self, *args, **kwargs):
        super(RefNumberForm, self).__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[name].help_text,
                })

    class Meta:
        model = RefNumber
        fields = ['holding_institution', 'refnumber_name', 'refnumber_title', 'collection_link']


#Form for adding a new Document to the Database
class DocumentTitleForm(forms.ModelForm):
    source_type_parent = forms.ModelChoiceField(
        queryset=SourceType.objects.filter(parent_type__isnull=True).order_by('type_name'),
        required=True,
        help_text='Ebene 1',
        label = 'Archivalienart',
        )
    source_type_child = forms.ModelChoiceField(
        queryset=SourceType.objects.filter(parent_type__isnull=False).order_by('type_name'),
        required=False,
        help_text='Ebene 2',
        widget=SourceChildSelect,
        )

    #add class form-control to each form input for bootstrap integration
    def __init__(self, *args, **kwargs):
        super(DocumentTitleForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            if isinstance(self.fields[name], forms.BooleanField):
                self.fields[name].widget.attrs.update({'class': 'form-check-input'})
            else:
                self.fields[name].widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': self.fields[name].help_text,
                    })
        
        self.fields['start_year'].widget.attrs.update({
            'min': -3000, #ToDo: Probably solve this with validators? Do the same for end_dates
            'max': datetime.now().year
            })

        #handle dependent dropdowns
        self.fields['parent_refnumber'].queryset = RefNumber.objects.none()

        if 'parent_institution' in self.data:
            try:
                institution_id = int(self.data.get('parent_institution'))
                self.fields['parent_refnumber'].queryset = RefNumber.objects.filter(holding_institution_id=institution_id).order_by('refnumber_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['parent_refnumber'].queryset = self.instance.holding_institution.refnumber_set.order_by('refnumber_name')

    class Meta:
        model = DocumentTitle
        fields = ['title_name',
                  'parent_institution',
                  'parent_refnumber',
                  'author',
                  'start_year',
                  'start_month',
                  'start_day',
                  'end_year',
                  'end_month',
                  'end_day',
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
                  'transcription_scope',
                  'comments',
                  'transcription_text',
                  'document_slug',
                  'submitted_by_anonymous',
                  ]


# Form for editing Metadata
class EditMetaForm(forms.ModelForm):
    source_type_parent = forms.ModelChoiceField(
        queryset=SourceType.objects.filter(parent_type__isnull=True).order_by('type_name'),
        required=True,
        help_text='Ebene 1',
        label = 'Archivalienart',
        )
    source_type_child = forms.ModelChoiceField(
        queryset=SourceType.objects.filter(parent_type__isnull=False).order_by('type_name'),
        required=False,
        help_text='Ebene 2',
        widget=SourceChildSelect,
        )


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
    
    class Meta:
        model = DocumentTitle
        fields = ['author',
                  'start_year',
                  'start_month',
                  'start_day',
                  'end_year',
                  'end_month',
                  'end_day',
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
                  'submitted_by_anonymous',
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

        
    class Meta:
        model = DocumentTitle
        fields = ['transcription_scope',
                  'transcription_text',
                  'commit_message',
                  'submitted_by_anonymous',
                  ]
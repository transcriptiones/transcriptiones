from bootstrap_modal_forms.forms import BSModalModelForm
from dal import autocomplete
from django import forms

from main.forms.forms_helper import initialize_form_helper
from main.models import Institution, \
    RefNumber, Document, SourceType, Author, Language


class InstSelectTestForm(forms.ModelForm):
    parent_institution = forms.ModelChoiceField(queryset=Institution.objects.all().order_by('institution_name'),
                                                widget=autocomplete.ModelSelect2(url='main:inst-autocomplete'))

    parent_ref_number = forms.ModelChoiceField(queryset=RefNumber.objects.all().order_by('ref_number_name'),
                                               widget=autocomplete.ModelSelect2(url='main:refn-autocomplete',
                                                                                forward=['parent_institution', ]))

    selection_helper_source_type = forms.ModelChoiceField(queryset=SourceType.objects.filter(parent_type=None).order_by('type_name'),
                                                          widget=autocomplete.ModelSelect2(url='main:srctype-autocomplete'))

    source_type = forms.ModelChoiceField(queryset=SourceType.objects.exclude(parent_type=None).order_by('type_name'),
                                         widget=autocomplete.ModelSelect2(url='main:srctype-ch-autocomplete',
                                                                          forward=['selection_helper_source_type', ]))

    author = forms.ModelMultipleChoiceField(queryset=Author.objects.all().order_by('author_name'),
                                            widget=autocomplete.ModelSelect2Multiple(url='main:author-autocomplete'))

    language = forms.ModelMultipleChoiceField(queryset=Language.objects.all().order_by('name_native'),
                                              widget=autocomplete.ModelSelect2Multiple(url='main:language-autocomplete'))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

    class Meta:
        model = Document
        exclude = ('institution_utc_add', 'document_slug', 'version_number', 'commit_message')


class InstModelForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

from bootstrap_modal_forms.forms import BSModalModelForm
from dal import autocomplete
from django import forms

from main.forms.forms_helper import initialize_form_helper
from main.models import Institution, \
    RefNumber, Document, SourceType, Author, Language


class RefnModelForm(BSModalModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

    class Meta:
        model = RefNumber
        fields = [
            'holding_institution',
            'ref_number_name',
            'ref_number_title',
            'collection_link']


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
            'site_url']

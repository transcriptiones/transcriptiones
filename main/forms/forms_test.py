from bootstrap_modal_forms.forms import BSModalModelForm
from dal import autocomplete
from django import forms

from main.forms.forms_helper import initialize_form_helper
from main.models import Institution, \
    RefNumber, Document, SourceType, Author, Language





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

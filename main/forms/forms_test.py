"""TODO"""
from bootstrap_modal_forms.forms import BSModalModelForm
from django import forms
from main.forms.forms_helper import initialize_form_helper
from main.models import Institution, RefNumber


class RefnModelForm(BSModalModelForm):
    """TODO """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = initialize_form_helper()

    holding_institution = forms.ModelChoiceField(queryset=Institution.objects.order_by('institution_name'))

    class Meta:
        model = RefNumber
        fields = [
            'holding_institution',
            'ref_number_name',
            'ref_number_title',
            'collection_link']


class InstModelForm(BSModalModelForm):
    """TODO """
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

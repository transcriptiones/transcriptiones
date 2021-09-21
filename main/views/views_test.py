from bsmodals import handle_form
from django.http import JsonResponse
from django.shortcuts import render
from dal import autocomplete
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from django.utils.translation import ugettext_lazy as _

from main.models import Institution, RefNumber, InstitutionSerializer
from main.forms.forms_upload import InstitutionForm
from main.model_info import get_extended_help_text


class InstitutionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Institution.objects.none()

        qs = Institution.objects.all()

        if self.q:
            qs = qs.filter(institution_name__icontains=self.q)

        return qs

    def post(self, request):
        i = Institution(institution_name=request.POST.get('text'))
        return i


class RefNumberAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return RefNumber.objects.none()

        qs = RefNumber.objects.all()
        selected_institution = self.forwarded.get('parent_institution', None)
        print(selected_institution)

        if not selected_institution:
            return []
        else:
            qs = qs.filter(holding_institution=selected_institution)

        if self.q:
            qs = qs.filter(ref_name__icontains=self.q)

        return qs


class InstitutionViewSet(viewsets.ModelViewSet):
    serializer_class = InstitutionSerializer
    queryset = Institution.objects.all()

    def create(self, request):
        #import pudb; pudb.set_trace()
        print('*** data', request.data);

        try:
            response = super().create(request)
            print('   response', response)
        except Exception as e:
            print('!!!', e)
            raise
        return response


def show_i18n(request):
    form = InstitutionForm()
    ht = get_extended_help_text(Institution, 'zip_code')
    context = {'form': form, 'v1': _('Paper'), 'v2': Institution.institution_name, 'v3': ht}
    return render(request, 'main/i18n_test.html', context=context)

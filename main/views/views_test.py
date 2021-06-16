from bootstrap_modal_forms.generic import BSModalCreateView
from bsmodals import handle_form
from django.http import JsonResponse
from django.shortcuts import render
from dal import autocomplete
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

from main.models import Institution, RefNumber, InstitutionSerializer
from main.forms.forms_upload import DocumentForm, InstitutionForm, InstitutionForm2


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


def test_bsmodals2(request):
    if request.method == "POST":
        print("POSTED!!!")

    return render(request, 'main/test_modals2.html')

def test_bsmodals3(request):
    return render(request, 'main/test_modals3.html')

def test_bsmodals(request):
    return render(request, 'main/test_modals.html')


class InstitutionCreateView(BSModalCreateView):
    template_name = 'main/tests/create_book.html'
    form_class = InstitutionForm2
    success_message = 'Success: Book was created.'
    success_url = reverse_lazy('main:test_modals')


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


def test_dropdown(request):
    form = DocumentForm()
    return render(request, 'main/test_dd.html', {'form': form})


@csrf_exempt
def create_institution(request):
    form = InstitutionForm(request.POST)

    # Uncomment to use real form handler
    result, data = handle_form(form)
    print('Handled form:', result, data)

    return JsonResponse(data)

def test(request):
    return render(request, 'main/test.html')


def institutions(request):
    data = dict()
    if request.method == 'GET':
        books = Institution.objects.all()
        data['table'] = render_to_string(
            'main/tests/_books_table.html',
            {'books': books},
            request=request
        )
        return JsonResponse(data)

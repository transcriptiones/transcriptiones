from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from bootstrap_modal_forms.generic import BSModalCreateView

from main.forms.forms_test import InstModelForm, RefnModelForm
from main.forms.forms_upload import UploadTranscriptionForm, BatchUploadForm
from main.models import Document, Institution, RefNumber


def upload_options(request):
    return render(request, 'main/upload/upload_options.html')


@login_required
def upload_multiple_transcriptions_view(request):
    return render(request, 'main/upload/create_multiple_documents.html')


@login_required
def upload_batch_view(request):
    form = BatchUploadForm()
    return render(request, 'main/upload/create_batch_contact.html', {'form': form})


@login_required
def upload_transcription_view(request):
    """This view shows the upload form."""
    form = UploadTranscriptionForm()
    context = {'insts': Institution.objects.all(), 'form': form}

    if request.method == "POST":
        form = UploadTranscriptionForm(request.POST)

        if form.is_valid():
            new_document = form.save(commit=False)
            new_document.document_slug = slugify(new_document.title_name)
            new_document.submitted_by = request.user
            new_document.active = True
            new_document.commit_message = 'Initial commit'
            new_document.version_number = 1

            if new_document.material == '':
                new_document.material = None

            if new_document.paging_system == '':
                new_document.paging_system = None

            new_document.save()
            messages.success(request, _('The document has been created.'))
            return HttpResponseRedirect(reverse('main:thank_you', kwargs={'doc_id': new_document.id}))
        else:
            print("NOT VALID")
            print(form.errors)
            what = {'csrfmiddlewaretoken': ['a4spkadinbV0bl0tQWhXvacKNCu5HHwIqz4PwkXnzuOEYvJiuaZslgN4CWaaAsGL'],
                    'title_name': ['My First Document'],
                    'parent_institution': ['1'],
                    'parent_ref_number': ['1'],
                    'transcription_scope': ['yxcyc'],
                    'doc_start_date': ['1916'],
                    'doc_end_date': [''],
                    'place_name': ['Basel'],
                    'transcription_text': ['<p>yxcyxcyxcyxcyxc</p>\r\n'],
                    'author': ['302'],
                    'material': [''],
                    'measurements_length': [''],
                    'measurements_width': [''],
                    'pages': [''],
                    'paging_system': [''],
                    'illuminated': ['unknown'],
                    'seal': ['unknown'],
                    'comments': ['']}

    return render(request, 'main/upload/create_document.html', context)


class ModalCreateInstitutionView(BSModalCreateView):
    """Creates a bootstrap modal view to create an institution."""
    template_name = 'main/upload/create_institution.html'
    form_class = InstModelForm
    success_message = _('Success: Institution was created.')
    success_url = reverse_lazy('main:upload_document')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.institution_slug = slugify(self.object.institution_name)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class ModalCreateRefNumberView(BSModalCreateView):
    """Creates a bootstrap modal view to create a reference number."""
    template_name = 'main/upload/create_ref_number.html'
    form_class = RefnModelForm
    success_message = _('Success: RefNumber was created.')
    success_url = reverse_lazy('main:upload_document')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.ref_number_slug = slugify(self.object.ref_number_name + " " + self.object.ref_number_title)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


def institution_dropdown_view(request):
    """Creates a SELECT view for the institutions"""
    data = dict()
    if request.method == 'GET':
        institutions = Institution.objects.all().order_by('institution_name')
        data['select'] = render_to_string(
            'main/upload/_inst_dropdown.html',
            {'insts': institutions},
            request=request
        )
        return JsonResponse(data)


def refnumber_dropdown_view(request):
    """Creates a SELECT view for the reference numbers"""
    data = dict()
    if request.method == 'GET':
        ref_numbers = RefNumber.objects.all().order_by('ref_number_name')
        data['select'] = render_to_string(
            'main/upload/_refn_dropdown.html',
            {'refns': ref_numbers},
            request=request
        )
        return JsonResponse(data)


def thanks_view(request, doc_id):
    """View to display after successful transcription upload"""
    try:
        document = Document.objects.get(id=doc_id)
    except Document.DoesNotExist:
        document = None

    context = {'document': document}
    template_name = "main/upload/thank_you.html"
    return render(request, template_name, context)

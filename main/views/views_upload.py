from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from bootstrap_modal_forms.generic import BSModalCreateView

from main.mail_utils import send_contact_message_copy
from main.forms.forms_upload import UploadTranscriptionForm, BatchUploadForm, InstModelForm, RefnModelForm
from main.models import Document, Institution, RefNumber, ContactMessage


def upload_options(request):
    return render(request, 'main/upload/upload_options.html')


@login_required
def upload_multiple_transcriptions_view(request):
    return render(request, 'main/upload/create_multiple_documents.html')


@login_required
def upload_batch_view(request):
    form = BatchUploadForm()

    if request.method == "POST":
        form = BatchUploadForm(request.POST)
        if form.is_valid():
            new_message = ContactMessage.objects.create(reply_email=request.user.email,
                                                        subject=form.cleaned_data['batch_title'],
                                                        message=form.cleaned_data['batch_description'])
            send_contact_message_copy(request, new_message)
            messages.success(request, _('Your Message has been sent. You received a copy by email.'))
            return redirect('main:upload_options')

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
            max_slug_length_title_name = new_document.title_name
            if len(max_slug_length_title_name) > 50:
                max_slug_length_title_name = max_slug_length_title_name[:49]

            new_slug = slugify(max_slug_length_title_name)
            inc_value = 1
            while Document.objects.filter(document_slug=new_slug).count() != 0:
                new_slug = new_slug[:40] + f"-{inc_value}"
                inc_value += 1
                if inc_value >= 10:
                    messages.error(request, _("There are many different documents with very similar titles. "
                                              "Please choose another title or contact transcriptiones."))
                    context = {'insts': Institution.objects.all(), 'form': form}
                    return render(request, 'main/upload/create_document.html', context)

            new_document.document_slug = new_slug
            new_document.submitted_by = request.user
            new_document.active = True
            new_document.commit_message = 'Initial commit'
            new_document.version_number = 1

            # User is asked if he wants to stay anonymous. (Anonymous = Field is True)
            # What we save is if we the publish the user. (Anonymous = Field is False)
            # Therefore we switch values
            new_document.publish_user = not new_document.publish_user

            if new_document.material == '':
                new_document.material = None

            if new_document.paging_system == '':
                new_document.paging_system = None

            new_document.save()

            for language in form.cleaned_data['language'].all():
                new_document.language.add(language)

            for author in form.cleaned_data['author'].all():
                new_document.author.add(author)

            messages.success(request, _('The document has been created.'))
            return HttpResponseRedirect(reverse('main:thank_you', kwargs={'doc_id': new_document.id}))
        else:
            messages.error(request, _("There is an error in your form"))
            context = {'insts': Institution.objects.all(), 'form': form}
            #print("NOT VALID")
            #print(form.errors)

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
        self.object.created_by = self.request.user
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
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    """def get_initial(self):
        initial = {
            'ref_number_name': self.request.GET.get('name', 'blank value')
        }
        return initial"""


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

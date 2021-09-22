from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from main.forms.forms_edit import EditTranscriptionForm, EditMetaForm
from main.models import Document


@login_required
def edit_transcription_view(request, inst_slug, ref_slug, doc_slug):
    document = Document.objects.get(document_slug=doc_slug)
    document.commit_message = ''
    old_transcription = document.transcription_text
    form = EditTranscriptionForm(instance=document)

    if request.method == "POST":
        form = EditTranscriptionForm(request.POST)

        if form.is_valid():
            updated_data = form.save(commit=False)
            if updated_data.transcription_text != old_transcription:
                document.transcription_text = updated_data.transcription_text
                document.commit_message = updated_data.commit_message
                document.submitted_by = request.user
                document.save()
                messages.success(request, _('The document has been updated.'))
                return HttpResponseRedirect(reverse('main:document_detail', kwargs={'inst_slug': inst_slug,
                                                                                    'ref_slug': ref_slug,
                                                                                    'doc_slug': doc_slug}))
            # If the transcription did not change: do not save
            else:
                messages.warning(request, _('The transcription did not change. No new version saved.'))
                return HttpResponseRedirect(reverse('main:document_detail', kwargs={'inst_slug': inst_slug,
                                                                                    'ref_slug': ref_slug,
                                                                                    'doc_slug': doc_slug}))
        else:
            print("invalid")

    context = {'document': document, 'form': form}
    return render(request, 'main/upload/edit_document_transcription.html', context)


@login_required
def edit_meta_view(request, inst_slug, ref_slug, doc_slug):
    document = Document.objects.get(document_slug=doc_slug)
    form = EditMetaForm(instance=document)
    context = {'document': document, 'form': form}
    return render(request, 'main/upload/edit_meta.html', context)

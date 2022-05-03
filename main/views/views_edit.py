from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
import main.model_info as m_info
from main.forms.forms_edit import EditTranscriptionForm, EditMetaForm
from main.models import Document
from main.tables.tables_base import TitleValueTable


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
            # TODO print("invalid")
            pass

    context = {'document': document, 'form': form}
    return render(request, 'main/upload/edit_document_transcription.html', context)


@login_required
def edit_meta_view(request, inst_slug, ref_slug, doc_slug):
    document = Document.objects.get(document_slug=doc_slug)
    document.commit_message = ''
    form = EditMetaForm(instance=document)
    form.fields['selection_helper_source_type'].initial = document.source_type.parent_type
    table = TitleValueTable(data=m_info.get_document_meta_edit_info(document))
    context = {'document': document, 'table': table, 'form': form}

    if request.method == "POST":
        form = EditMetaForm(request.POST)

        if form.is_valid():
            updated_data = form.save(commit=False)
            document.transcription_scope = updated_data.transcription_scope
            document.doc_start_date = updated_data.doc_start_date
            document.doc_end_date = updated_data.doc_end_date
            document.place_name = updated_data.place_name
            document.source_type = updated_data.source_type
            # document.author = updated_data.author
            # document.language = updated_data.language
            document.material = updated_data.material
            document.measurements_length = updated_data.measurements_length
            document.measurements_width = updated_data.measurements_width
            document.pages = updated_data.pages
            document.paging_system = updated_data.paging_system
            document.illuminated = updated_data.illuminated
            document.seal = updated_data.seal
            document.commit_message = updated_data.commit_message
            document.submitted_by = request.user
            document.publish_user = not request.user.is_anonymous

            document.save()

            for language in form.cleaned_data['language'].all():
                document.language.add(language)

            for author in form.cleaned_data['author'].all():
                document.author.add(author)

            messages.success(request, _('The metadata of the document has been updated.'))
            return HttpResponseRedirect(reverse('main:document_detail', kwargs={'inst_slug': inst_slug,
                                                                                'ref_slug': ref_slug,
                                                                                'doc_slug': doc_slug}))
        else:
            # TODO print(form.errors)
            messages.error(request, 'FORM INVALID')

    return render(request, 'main/upload/edit_meta.html', context)

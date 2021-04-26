from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from main.models import Document


class DocumentExportView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'main/upload/export_document.html'
    context_object_name = 'document'

    # get object to update
    def get_object(self):
        institution = self.kwargs.get('inst_slug')
        ref_number = self.kwargs.get('ref_slug')
        document = self.kwargs.get('doc_slug')
        queryset = Document.objects.filter(parent_institution__institution_slug=institution)
        queryset = queryset.filter(parent_ref_number__ref_number_slug=ref_number)
        return queryset.get(document_slug=document)

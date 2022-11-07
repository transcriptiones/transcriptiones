from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import DetailView
import easy_pdf.rendering

from main.export import export
from main.models import Document


class DocumentExportView(DetailView):
    model = Document
    template_name = 'main/upload/export_document.html'
    context_object_name = 'document'

    def get_object(self):
        institution = self.kwargs.get('inst_slug')
        ref_number = self.kwargs.get('ref_slug')
        document = self.kwargs.get('doc_slug')
        queryset = Document.objects.filter(parent_ref_number__holding_institution__institution_slug=institution)
        queryset = queryset.filter(parent_ref_number__ref_number_slug=ref_number)
        return queryset.get(document_slug=document)

    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            document = self.get_object()
            file_name = f'transcriptiones_export_{document.id}'

            if 'export_tei' in self.request.POST.keys():
                file_contents = export(document, export_type='tei')
                content_type = 'text/xml'
                file_ending = 'tei'
            elif 'export_json' in self.request.POST.keys():
                file_contents = export(document, export_type='json')
                content_type = 'application/json'
                file_ending = 'json'
            elif 'export_html' in self.request.POST.keys():
                file_contents = export(document, export_type='html')
                content_type = 'text/html'
                file_ending = 'html'
            elif 'export_pdf' in self.request.POST.keys():
                file_contents = export(document, export_type='pdf')
                content_type = 'application/pdf'
                file_ending = 'pdf'
                file_contents = easy_pdf.rendering.render_to_pdf('main/pdf_export_template.html', {'contents': file_contents})
            elif 'export_txt' in self.request.POST.keys():
                file_contents = export(document, export_type='txt')
                content_type = 'text/plain'
                file_ending = 'txt'
            else:
                file_contents = 'Invalid Export Function Selected'
                content_type = 'text/plain'
                file_ending = 'txt'

        response = HttpResponse(file_contents, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename={file_name}.{file_ending}'
        return response

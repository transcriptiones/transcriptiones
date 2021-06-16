from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import generic
from django.template.defaultfilters import slugify

from bootstrap_modal_forms.generic import BSModalCreateView

from main.forms.forms_test import InstModelForm, InstSelectTestForm
from main.models import Institution, RefNumber, SourceType, Author, Language


class IndexInst(generic.ListView):
    model = Institution
    context_object_name = 'insts'
    template_name = 'main/tests2/inst.html'


def new_index_inst(request):
    form = InstSelectTestForm()
    context = {'insts': Institution.objects.all(), 'form': form}

    if request.method == "POST":
        form = InstSelectTestForm(request.POST)

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

    return render(request, 'main/tests2/inst.html', context)


class InstCreateView(BSModalCreateView):
    template_name = 'main/tests2/create_inst.html'
    form_class = InstModelForm
    success_message = 'Success: Inst was created.'
    success_url = reverse_lazy('main:index_inst')


def insts(request):
    data = dict()
    if request.method == 'GET':
        insts = Institution.objects.all().order_by('institution_name')
        data['select'] = render_to_string(
            'main/tests2/_inst_dropdown.html',
            {'insts': insts},
            request=request
        )
        return JsonResponse(data)

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.views.generic import UpdateView
from django.utils.text import slugify
from django.contrib.auth.mixins import LoginRequiredMixin
from main.forms.forms_upload import InstitutionForm, RefNumberForm, DocumentForm, EditMetaForm, EditTranscriptForm
from main.models import Author, Institution, RefNumber, Document, SourceType
from main.utils import create_related_objects
from bootstrap_modal_forms.generic import BSModalCreateView
from django.urls import reverse_lazy


class AddInstitutionView(LoginRequiredMixin, BSModalCreateView):
    """View for adding institution"""

    form_class = InstitutionForm
    template_name = "main/upload/add_institution.html"
    success_message = 'Success: Book was created.'
    success_url = reverse_lazy('main:start')

    """
    # display form if accessed via GET
    def get(self, *args, **kwargs):
        if self.request.method == "GET":
            form = self.form_class()
            return render(self.request, self.template_name,
                          {"form": form})

    
    # handle the form if accessed via POST
    def post(self, *args, **kwargs):
        if self.request.is_ajax and self.request.method == "POST":            
            institution_name = self.request.POST.get('new_institution_name')
            street = self.request.POST.get('new_street')
            zip_code = self.request.POST.get('new_zip_code')
            city = self.request.POST.get('new_city')
            country = self.request.POST.get('new_country')
            site_url = self.request.POST.get('new_site_url')
            institution_slug = slugify(institution_name)

            #
            # Do we need server-side validation here?
            #

            Institution.objects.create(
                institution_name = institution_name,
                street = street,
                zip_code = zip_code,
                city = city,
                country = country,
                site_url = site_url,
                institution_slug = institution_slug
                )

            institutions = Institution.objects.all()

            return render(self.request, 'upload/inst_dropdown_options.html', {'institutions': institutions})
    """


class AddRefNumberView(LoginRequiredMixin, View):
    """View for adding RefNumber"""
    form_class = RefNumberForm
    template_name = "main/upload/add_ref_number.html"

    # Display form if accessed via GET
    def get(self, *args, **kwargs):
        if self.request.method =="GET":
            form = self.form_class()
            return render(self.request, self.template_name,
                          {"form": form})

    # Handle the form if accessed via POST
    def post(self, *args, **kwargs):
        if self.request.is_ajax and self.request.method == "POST":            
            holding_institution = Institution.objects.get(id=self.request.POST.get('new_holding_institution'))
            refnumber_name = self.request.POST.get('new_refnumber_name')
            refnumber_title = self.request.POST.get('new_refnumber_title')
            collection_link = self.request.POST.get('new_collection_link')
            refnumber_slug = slugify(refnumber_name)
           
            #
            #Do we need server-side validation here?
            #

            RefNumber.objects.create(
                holding_institution = holding_institution,
                refnumber_name = refnumber_name,
                refnumber_title = refnumber_title,
                collection_link = collection_link,
                refnumber_slug = refnumber_slug
                )

            refnumbers = RefNumber.objects.filter(holding_institution_id=holding_institution).order_by('holding_institution')

            return render(self.request, 'upload/ref_dropdown_options.html', {'refnumbers': refnumbers})


class AddDocumentView(LoginRequiredMixin, View):
    """View for creating new document object"""

    form_class = DocumentForm
    template_name = "main/upload/add_document_form.html"

    # Display the form if accessed via GET
    def get(self, *args, **kwargs):
        if self.request.method == "GET":
            # Pre-populate field if user wants to publish anonymously
            if self.request.user.mark_anonymous:
                form = self.form_class(initial={'publish_user': True})
            else:
                form = self.form_class()
            return render(self.request, self.template_name, {"form": form})

    # handle the form if accessed via POST
    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            print('in post')
            data = self.request.POST.copy()
            
            # If there are authors in the formdata, add new authors to db
            create_related_objects(listname="author",
                                   formdata=data,
                                   relatedclass=Author,
                                   namefield="author_name"
                                   )

            document_slug = slugify(data.get("title_name"))
            data["document_slug"] = document_slug

            document = Document(submitted_by=self.request.user)  # Set submitter to current user

            # set source_type based on selection
            if 'source_type_child' in data:
                document.source_type = SourceType.objects.get(pk=data['source_type_child'])
            elif 'source_type_child' not in data:
                document.source_type = SourceType.objects.get(pk=data['source_type_parent'])

            form = self.form_class(data, instance=document)

            if form.is_valid():
                createdobj = form.save()
                context = {'object': createdobj}
                response = thanks_view(self.request, context)
                return response

            else:
                return HttpResponse(str(form.errors).encode())
                # TODO CHECK
                # Exception Handling goes here!
                # return render(self.request, self.template_name, {"form": form})


def thanks_view(request, context):
    """View to display after successful form-submit"""
    template_name = "main/upload/form_redirect.html"
    return render(request, template_name, context)
    

def load_ref_numbers(request):
    """View for loading ref numbers, depending on chosen Institution"""
    institution_id = request.GET.get('institution')

    ref_numbers = RefNumber.objects.filter(holding_institution_id=institution_id).order_by('holding_institution')
    return render(request, 'main/upload/ref_dropdown_options.html', {'ref_numbers': ref_numbers})


# Base class for Editing DocumentTitle objects
class BaseEditDocumentView(LoginRequiredMixin, UpdateView):
    model = Document

    # get object to update
    def get_object(self):
        institution = self.kwargs.get('inst_slug')
        ref_number = self.kwargs.get('ref_slug')
        document = self.kwargs.get('doc_slug')
        queryset = Document.objects.filter(parent_ref_number__holding_institution__institution_slug=institution)
        queryset = queryset.filter(parent_ref_number__ref_number_slug=ref_number)
        return queryset.get(document_slug=document)

    # update form data if accessed via GET
    def get_context_data(self, **kwargs):
        if self.request.method == "GET":
            # get object and clear field commit_message
            context = super().get_context_data(**kwargs)
            document = self.get_object()
            document.commit_message = ''

            # prepopulate field publish_user
            if self.request.user.mark_anonymous:
                document.publish_user = True

            form = self.form_class(instance=document)

            context['form'] = form
            return context

        return super().get_context_data(**kwargs)


class EditMetaView(BaseEditDocumentView):
    """View for editing Metadata"""

    form_class = EditMetaForm
    template_name = "main/upload/edit_meta.html"

    def get_context_data(self, **kwargs):
        if self.request.method == "GET":
            context = super().get_context_data(**kwargs)

            # prepopulate source_type_parent and source_type_child
            if self.get_object().source_type.parent_type is None:
                context['form'].fields['source_type_parent'].initial = self.get_object().source_type.pk
            else:
                context['form'].fields['source_type_parent'].initial = self.get_object().source_type.parent_type.pk
                context['form'].fields['source_type_child'].initial = self.get_object().source_type.pk

            return context
        return super().get_context_data(**kwargs)

    # Handle the form if accesed via POST
    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            data = self.request.POST.copy()
            
            # If there are authors in the formdata, add new authors to db
            create_related_objects(listname="author",
                                   formdata=data,
                                   relatedclass=Author,
                                   namefield="author_name"
                                   )

            document = self.get_object()
            document.submitted_by = self.request.user

            # set source_type based on selection
            if 'source_type_child' in data:
                document.source_type = SourceType.objects.get(pk=data['source_type_child'])
            elif not 'source_type_child' in data:
                document.source_type = SourceType.objects.get(pk=data['source_type_parent'])

            form = self.form_class(data, instance=document)

            if form.is_valid():
                createdobj = form.save()
                context = {'object': createdobj}
                response = thanks_view(self.request, context)
                return response
            else:
                return HttpResponse(str(form.errors).encode())
                #Exception Handling goes here!
                #
                #return render(self.request, self.template_name,
                #          {"form": form})


# View for editing Transcript
class EditTranscriptView(BaseEditDocumentView):
    form_class = EditTranscriptForm
    template_name = "main/upload/edit_transcript.html"
    
    # Handle the form if accessed via POST
    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            document = self.get_object()
            document.submitted_by = self.request.user
            
            print(document.author.all()) # Output: <QuerySet [<Author: Theophil Läppli>]>

            form = self.form_class(self.request.POST, instance=document)
            print(form.data.get('author')) # Output: None

            if form.is_valid():
                print(form.cleaned_data.get('author')) # Output: <QuerySet []>
                createdobj = form.save()
                print(createdobj.author.all()) # Output: <QuerySet []>
                context = {'object': createdobj}
                response = thanks_view(self.request, context)
                return response
            else:
                return HttpResponse(str(form.errors).encode())
                #Exception Handling goes here!
                #
                #return render(self.request, self.template_name,
                #          {"form": form})


# View for creating multiple objects from csv-File
def batch_upload(request):
    template_name = 'main/upload/batch_upload.html'
    errors = {}
    if request.method == 'GET':
        return render(request, template_name)

    if request.method == 'POST':
        try:
            csv_file = request.FILES['csv_file']
            
            # check if file is csv
            if not csv_file.name.endswith('.csv'):
                errors['filetypeerror'] = "File ist keine CSV-Datei"
            
            # check if file is not bigger than 2.5 MB
            if csv_file.multiple_chunks():
                errors['filetoolarge'] = "File ist zu gross"
            
            # if checks have failed, return the form with errors
            if len(errors) != 0:
                return render(request, template_name, {'errors': errors})

            # read csv and split it into lines
            file_data = csv_file.read().decode('utf-8')
            lines = file_data.split("\n")

            # handle batch upload for SourceTypes
            if request.POST.get('target_model') == 'SourceType':
                for line in lines:
                    fields = line.strip('\r').split(";")
                    
                    # ignore lines without type_name
                    if fields[0] == '':
                        continue

                    # if parent is set, get parent object from db and create new child object
                    elif fields[1] != '':
                        type_name = str(fields[0])
                        parent_name = str(fields[1])
                        parent_id = SourceType.objects.get(type_name=parent_name)
                        SourceType.objects.create(
                            type_name = type_name,
                            parent_type = parent_id
                            )
                    
                    # if no parent is set, create new object
                    else:
                        type_name = str(fields[0])
                        SourceType.objects.create(type_name=type_name)

                return redirect('start')

            return redirect('start')

        except Exception as e:
            return HttpResponse(str(e))


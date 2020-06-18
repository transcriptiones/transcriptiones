import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.views import View
from django.views.generic import TemplateView, UpdateView
from django.utils.text import slugify
from django.contrib.auth.mixins import LoginRequiredMixin
from transcripta.transcripts.forms import InstitutionForm, RefNumberForm, DocumentTitleForm, EditMetaForm, EditTranscriptForm
from transcripta.transcripts.models import Author, Institution, RefNumber, DocumentTitle, SourceType
from transcripta.transcripts.utils import create_related_objects


# Create your views here.

#View for adding institution
class AddInstitutionView(LoginRequiredMixin, View):
    form_class = InstitutionForm
    template_name = "upload/addinstitution.html"

    #display form if accessed via GET
    def get(self, *args, **kwargs):
        if self.request.method == "GET":
            form = self.form_class()
            return render(self.request, self.template_name,
                          {"form": form})

    #handle the form if accessed via POST
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
            #Do we need server-side validation here?
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

#View for adding RefNumber
class AddRefNumberView(LoginRequiredMixin, View):
    form_class = RefNumberForm
    template_name = "upload/addrefnumber.html"

    #display form if accessed via GET
    def get(self, *args, **kwargs):
        if self.request.method =="GET":
            form = self.form_class()
            return render(self.request, self.template_name,
                          {"form": form})

    #handle the form if accessed via POST
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


#View for creating new document object
class AddDocumentView(LoginRequiredMixin, View):
    form_class = DocumentTitleForm
    template_name = "upload/documenttitle_form.html"

    # display the form if accessed via GET
    def get(self, *args, **kwargs):
        if self.request.method == "GET":
            # prepopulate field if user wants to publish anonymously
            if self.request.user.anonymous_publication:
                form = self.form_class(initial={'submitted_by_anonymous': True})
            else:
                form = self.form_class()
            return render(self.request, self.template_name, {"form": form})

    # handle the form if accessed via POST
    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            data = self.request.POST.copy()
            
            #if there are authors in the formdata, add new authors to db
            create_related_objects(listname="author",
                                   formdata=data,
                                   relatedclass=Author,
                                   namefield="author_name"
                                   )

            document_slug = slugify(data.get("title_name"))
            data["document_slug"] = document_slug

            document = DocumentTitle(submitted_by=self.request.user)  # Set submitter to current user

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


#View to display after successful form-submit
def thanks_view(request, context):
    template_name = "upload/formredirect.html"

    return render(request, template_name, context)
    
    
#View for loading refnumbers, depending on chosen Institution
def load_refnumbers(request):
    institution_id = request.GET.get('institution')

    refnumbers = RefNumber.objects.filter(holding_institution_id=institution_id).order_by('holding_institution')
    return render(request, 'upload/ref_dropdown_options.html', {'refnumbers': refnumbers})


# Base class for Editing DocumentTitle objects
class BaseEditDocumentView(LoginRequiredMixin, UpdateView):
    model = DocumentTitle

    # get object to update
    def get_object(self):
        institution = self.kwargs.get('instslug')
        refnumber = self.kwargs.get('refslug')
        document = self.kwargs.get('docslug')
        queryset = DocumentTitle.objects.filter(parent_institution__institution_slug = institution)
        queryset = queryset.filter(parent_refnumber__refnumber_slug = refnumber)
        return queryset.get(document_slug = document)

    # update form data if accessed via GET
    def get_context_data(self, **kwargs):
        if self.request.method == "GET":
            # get object and clear field commit_message
            context = super().get_context_data(**kwargs)
            document = self.get_object()
            document.commit_message = ''

            # prepopulate field submitted_by_anonymous
            if self.request.user.anonymous_publication:
                document.submitted_by_anonymous = True

            form = self.form_class(instance=document)

            context['form'] = form
            return context

        return super().get_context_data(**kwargs)



# view for editing Metadata
class EditMetaView(BaseEditDocumentView):
    form_class = EditMetaForm
    template_name = "upload/editmeta.html"

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


    #handle the form if accesed via POST
    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            data = self.request.POST.copy()
            
            #if there are authors in the formdata, add new authors to db
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
    template_name = "upload/edittranscript.html"
    
    #handle the form if accesed via POST
    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            document = self.get_object()
            document.submitted_by = self.request.user

            form = self.form_class(self.request.POST, instance=document)

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


# View for creating multiple objects from csv-File
def batchupload(request):
    template_name = 'upload/batchupload.html'
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

                return redirect('thanks')

            return redirect('start')

        except Exception as e:
            return HttpResponse(str(e))
            

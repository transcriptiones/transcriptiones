import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.views import View
from django.views.generic import TemplateView, UpdateView
from django.utils.text import slugify
from transcripta.transcripts.forms import InstitutionForm, RefNumberForm, DocumentTitleForm, EditMetaForm, EditTranscriptForm
from transcripta.transcripts.models import Author, Institution, RefNumber, DocumentTitle
from transcripta.transcripts.utils import create_related_objects


# Create your views here.

#View for adding institution
class AddInstitutionView(View):
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
class AddRefNumberView(View):
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
class AddDocumentView(View):
    form_class = DocumentTitleForm
    template_name = "upload/documenttitle_form.html"

    #display the form if accessed via GET
    def get(self, *args, **kwargs):
        if self.request.method == "GET":
            # prepopulate field if user wants to publish anonymously
            if self.request.user.anonymous_publication:
                form = self.form_class(initial={'submitted_by_anonymous': True})
            else:
                form = self.form_class()
            return render(self.request, self.template_name, {"form": form})

    #handle the form if accessed via POST
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
            form = self.form_class(data, instance=document)

            if form.is_valid():
                form.save()
                return redirect('thanks')

            else:
                return HttpResponse(str(form.errors).encode())
                #Exception Handling goes here!
                #
                #return render(self.request, self.template_name,
                #          {"form": form})


#View to display after successful form-submit
class RedirectView(TemplateView):
    template_name = "upload/formredirect.html"
    
    
#View for loading refnumbers, depending on chosen Institution
def load_refnumbers(request):
    institution_id = request.GET.get('institution')

    refnumbers = RefNumber.objects.filter(holding_institution_id=institution_id).order_by('holding_institution')
    return render(request, 'upload/ref_dropdown_options.html', {'refnumbers': refnumbers})


# view for editing Metadata
# maybe write abstract class EditView and subclass for Metadata and Transcript?
class EditMetaView(UpdateView):
    model = DocumentTitle
    form_class = EditMetaForm
    template_name = "upload/editmeta.html"

    # get object to update
    def get_object(self):
        institution = self.kwargs.get('instslug')
        refnumber = self.kwargs.get('refslug')
        document = self.kwargs.get('docslug')
        queryset = DocumentTitle.objects.filter(parent_institution__institution_slug = institution)
        queryset = queryset.filter(parent_refnumber__refnumber_slug = refnumber)
        return queryset.get(document_slug = document)

    def get_context_data(self, **kwargs):
        # if accessed via GET, clear field commit_message
        if self.request.method == "GET":
            context = super().get_context_data(**kwargs)
            document = self.get_object()
            document.commit_message = ''

            # prepopulate field if user wants to publish anonymously
            if self.request.user.anonymous_publication:
                document.submitted_by_anonymous = True

            form = self.form_class(instance=document)
            context['form'] = form
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

            form = self.form_class(data, instance=document)

            if form.is_valid():
                form.save()
                return redirect('thanks')
            else:
                return HttpResponse(str(form.errors).encode())
                #Exception Handling goes here!
                #
                #return render(self.request, self.template_name,
                #          {"form": form})


# View for editing Transcript
class EditTranscriptView(UpdateView):
    model = DocumentTitle
    form_class = EditTranscriptForm
    template_name = "upload/edittranscript.html"

    # get object to update
    def get_object(self):
        institution = self.kwargs.get('instslug')
        refnumber = self.kwargs.get('refslug')
        document = self.kwargs.get('docslug')
        queryset = DocumentTitle.objects.filter(parent_institution__institution_slug = institution)
        queryset = queryset.filter(parent_refnumber__refnumber_slug = refnumber)
        return queryset.get(document_slug = document)

    def get_context_data(self, **kwargs):
        # if accessed via GET, clear field commit_message
        if self.request.method == "GET":
            context = super().get_context_data(**kwargs)
            document = self.get_object()
            document.commit_message = ''

            # prepopulate field if user wants to publish anonymously
            if self.request.user.anonymous_publication:
                document.submitted_by_anonymous = True

            form = self.form_class(instance=document)
            context['form'] = form
            return context

        return super().get_context_data(**kwargs)
    
    #handle the form if accesed via POST
    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            document = self.get_object()
            document.submitted_by = self.request.user

            form = self.form_class(self.request.POST, instance=document)

            if form.is_valid():
                form.save()
                return redirect('thanks')
            else:
                return HttpResponse(str(form.errors).encode())
                #Exception Handling goes here!
                #
                #return render(self.request, self.template_name,
                #          {"form": form})
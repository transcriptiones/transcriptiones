import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.views import View
from django.views.generic import TemplateView
from django.utils.text import slugify
from transcripta.transcripts.forms import InstitutionForm, RefNumberForm, DocumentTitleForm
from transcripta.transcripts.models import Author, Institution, RefNumber, DocumentTitle


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
            form = self.form_class()
            return render(self.request, self.template_name,
                          {"form": form})

    #handle the form if accessed via POST
    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            data = self.request.POST.copy()
            
            #if there are authors in the formdata
            #add new authors to database
            #get list of new authors
            if "author" in data:
                authors = list()
                newauthors = list()
                for author in data.getlist("author"):
                    try: 
                        authors.append(int(author))
                    except ValueError:
                        newauthors.append(author)
                
                #create new author object for each element of the list.
                #append their pks to the list of authors from the form data
                for author in newauthors:
                    newauthor = Author.objects.create(
                        author_name = author
                        )
                    authors.append(newauthor.pk)

                data.setlist("author", authors)

            document_slug = slugify(data.get("title_name"))
            data["document_slug"] = document_slug

            document = DocumentTitle(submitted_by=self.request.user)  # Set submitter to current user
            form = self.form_class(data, instance=document)

            if form.is_valid():
                form.save()
                return HttpResponse('thanks')

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

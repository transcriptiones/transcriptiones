from django.urls import path
from transcripta.upload.views import AddInstitutionView, AddRefNumberView, AddDocumentView, RedirectView, load_refnumbers

urlpatterns = [
    path('', AddDocumentView.as_view(), name = 'document_add'),
    path('addinstitution/', AddInstitutionView.as_view(), name = 'institution_add'),
    path('addrefnumber/', AddRefNumberView.as_view(), name = 'refnumber_add'),
    path('ajax/load-refnumbers/', load_refnumbers, name = 'ajax_load_refnumbers'),
    path('thanks/', RedirectView.as_view(), name = 'thanks'),
    ]
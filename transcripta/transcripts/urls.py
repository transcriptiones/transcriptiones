from django.urls import path
from transcripta.transcripts.views import *


urlpatterns = [
    # urls for info views
    path('', StartView.as_view(), name = "start"),
    
    # urls for display views
    path('display/institutions/', InstitutionListView.as_view(), name = 'institutionlist'),
    path('display/<slug:instslug>/', InstitutionDetailView.as_view(), name = 'institutiondetail'),
    path('display/<slug:instslug>/<slug:refslug>/', RefNumberDetailView.as_view(), name = 'refnumberdetail'),
    path('display/<slug:instslug>/<slug:refslug>/<slug:docslug>/', DocumentTitleDetailView.as_view(), name='documenttitledetail'),

    # urls for upload views
    path('upload/', AddDocumentView.as_view(), name = 'document_add'),
    path('upload/addinstitution/', AddInstitutionView.as_view(), name = 'institution_add'),
    path('upload/addrefnumber/', AddRefNumberView.as_view(), name = 'refnumber_add'),
    path('upload/ajax/load-refnumbers/', load_refnumbers, name = 'ajax_load_refnumbers'),
    path('upload/thanks/', RedirectView.as_view(), name = 'thanks'),

    # urls for search views
    path('search/', SearchView.as_view(), name = 'searchform'),
    path('search/results/', ResultsView.as_view(), name='searchresults'),

    # urls for user views
    path('user/signup', signup, name = "signup"),
    path('user/activationsent', AccountActivationSentView.as_view(), name = "account_activation_sent"),
    path('user/activate/<uidb64>/<token>', activate, name = "activate"),

    ]
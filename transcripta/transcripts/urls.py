from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from transcripta.transcripts.views import *


urlpatterns = [
    # urls for info views
    path('', StartView.as_view(), name='start'),
    path('info/guidelines/', TemplateView.as_view(template_name='info/guidelines.html'), name='guidelines'),
    path('info/tos/', TemplateView.as_view(template_name='info/tos.html'), name='tos'),
    path('info/about/', TemplateView.as_view(template_name='info/about.html'), name='about'),
    path('info/aboutus/', TemplateView.as_view(template_name='info/aboutus.html'), name='aboutus'),
    path('info/contact/', TemplateView.as_view(template_name='info/contact.html'), name='contact'),
    
    # urls for display views
    path('display/institutions/', InstitutionListView.as_view(), name='institutionlist'),
    path('display/<slug:instslug>/', InstitutionDetailView.as_view(), name='institutiondetail'),
    path('display/<slug:instslug>/<slug:refslug>/', RefNumberDetailView.as_view(), name='refnumberdetail'),
    path('display/<slug:instslug>/<slug:refslug>/<slug:docslug>/', DocumentTitleDetailView.as_view(), name='documenttitledetail'),
    path('display/<slug:instslug>/<slug:refslug>/<slug:docslug>/<int:versionnr>/', DocumentTitleDetailView.as_view(), name='documenttitlelegacydetail'),
    path('display/<slug:instslug>/<slug:refslug>/<slug:docslug>/history/', DocumentHistoryView.as_view(), name='documenthistory'),
    
    # urls for upload views
    path('upload/', AddDocumentView.as_view(), name='document_add'),
    path('upload/addinstitution/', AddInstitutionView.as_view(), name='institution_add'),
    path('upload/addrefnumber/', AddRefNumberView.as_view(), name='refnumber_add'),
    path('upload/ajax/load-refnumbers/', load_refnumbers, name='ajax_load_refnumbers'),
    path('upload/thanks/', thanks_view, name='thanks'),
    path('upload/<slug:instslug>/<slug:refslug>/<slug:docslug>/editmeta/', EditMetaView.as_view(), name='editmeta'),
    path('upload/<slug:instslug>/<slug:refslug>/<slug:docslug>/edittranscript/', EditTranscriptView.as_view(), name='edittranscript'),
    path('upload/batch/', batchupload, name='batchupload'),

    # urls for search views
    path('search/', SearchView.as_view(), name='searchform'),
    path('search/results/', ResultsView.as_view(), name='searchresults'),

    # urls for user views
    path('user/signup/', signup, name='signup'),
    path('user/activationsent/', AccountActivationSentView.as_view(), name='account_activation_sent'),
    path('user/activate/<uidb64>/<token>/', activate, name='activate'),
    path('user/login/', CustomLoginView.as_view(), name='login'),
    path('user/logout/', LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('user/passwordchange/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('user/passwordchange/done/', PasswordChangeDoneView.as_view(template_name='users/passwordchangedone.html'), name='password_change_done'),
    path('user/profile/', userprofile, name='profile'),
    path('user/profile/update/', UserUpdateView.as_view(), name='user_update'),
    path('user/passwordreset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('user/passwordreset/done/', PasswordResetDoneView.as_view(template_name='users/passwordresetdone.html'), name='password_reset_done'),
    path('user/reset/<uidb64>/<token>/', CustomPasswordConfirmView.as_view(), name='password_reset_confirm'),
    path('user/reset/done/', PasswordResetCompleteView.as_view(template_name='users/passwordresetcomplete.html'), name='password_reset_complete'),
    ]
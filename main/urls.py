from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView, PasswordResetDoneView,\
    PasswordResetCompleteView

from main.views.views import test
from main.views.views import search, InstitutionListView
from main.views.views import InstitutionDetailView, RefNumberDetailView, DocumentDetailView, DocumentHistoryView
from main.views.views_upload import AddInstitutionView, AddRefNumberView, AddDocumentView, batch_upload, load_refnumbers
from main.views.views_upload import EditMetaView, EditTranscriptView
from main.views.views_upload import thanks_view
from main.views.views_user import signup, userprofile, UserUpdateView
from main.views.views_user import CustomLoginView
from main.views.views_user import activate, AccountActivationSentView
from main.views.views_user import CustomPasswordConfirmView, CustomPasswordResetView, CustomPasswordChangeView

app_name = 'main'
urlpatterns = [
    path('test/', test, name='test'),

    # urls for info views
    path('', TemplateView.as_view(template_name='main/info/start.html'), name='start'),
    path('info/guidelines/', TemplateView.as_view(template_name='main/info/guidelines.html'), name='guidelines'),
    path('info/tos/',        TemplateView.as_view(template_name='main/info/tos.html'),        name='tos'),
    path('info/about/',      TemplateView.as_view(template_name='main/info/about.html'),      name='about'),
    path('info/aboutus/',    TemplateView.as_view(template_name='main/info/about_us.html'),   name='about_us'),
    path('info/contact/',    TemplateView.as_view(template_name='main/info/contact.html'),    name='contact'),

    # urls for display views
    path('display/institutions/', InstitutionListView.as_view(), name='institution_list'),
    path('display/<slug:inst_slug>/', InstitutionDetailView.as_view(), name='institution_detail'),
    path('display/<slug:inst_slug>/<slug:ref_slug>/', RefNumberDetailView.as_view(), name='ref_number_detail'),
    path('display/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/', DocumentDetailView.as_view(),
         name='document_detail'),

    path('display/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/<int:version_nr>/', DocumentDetailView.as_view(), name='document_legacy_detail'),
    path('display/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/history/', DocumentHistoryView.as_view(), name='document_history'),

    # urls for upload views
    path('upload/', AddDocumentView.as_view(), name='upload_document'),
    path('upload/addinstitution/', AddInstitutionView.as_view(), name='institution_add'),
    path('upload/addrefnumber/', AddRefNumberView.as_view(), name='ref_number_add'),
    path('upload/ajax/load-refnumbers/', load_refnumbers, name='ajax_load_ref_numbers'),
    path('upload/thanks/', thanks_view, name='thanks'),
    path('upload/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/editmeta/', EditMetaView.as_view(), name='edit_meta'),
    path('upload/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/edittranscript/', EditTranscriptView.as_view(), name='edit_transcript'),
    path('upload/batch/', batch_upload, name='batch_upload'),

    # urls for search views
    path('search/', search, name='search'),
    path('search/', TemplateView.as_view(template_name='main/dummy.html'), name='search'),

    # urls for user views
    path('user/signup/', signup, name='signup'),
    path('user/activationsent/', AccountActivationSentView.as_view(), name='account_activation_sent'),
    path('user/activate/<uidb64>/<token>/', activate, name='activate'),
    path('user/login/', CustomLoginView.as_view(), name='login'),
    path('user/logout/', LogoutView.as_view(template_name='main/users/logout.html'), name='logout'),
    path('user/passwordchange/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('user/passwordchange/done/', PasswordChangeDoneView.as_view(template_name='main/users/password_change_done.html'), name='password_change_done'),
    path('user/profile/', userprofile, name='profile'),
    path('user/profile/update/', UserUpdateView.as_view(), name='user_update'),
    path('user/passwordreset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('user/passwordreset/done/', PasswordResetDoneView.as_view(template_name='main/users/password_reset_done.html'), name='password_reset_done'),
    path('user/reset/<uidb64>/<token>/', CustomPasswordConfirmView.as_view(), name='password_reset_confirm'),
    path('user/reset/done/', PasswordResetCompleteView.as_view(template_name='main/users/password_reset_complete.html'), name='password_reset_complete'),
    ]

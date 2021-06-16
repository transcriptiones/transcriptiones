from dal import autocomplete
from django.conf.urls import url
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView, PasswordResetDoneView,\
    PasswordResetCompleteView
from rest_framework.routers import DefaultRouter

from main.views.views_test import test, test_dropdown, test_bsmodals, test_bsmodals2, test_bsmodals3, InstitutionAutocomplete, RefNumberAutocomplete, InstitutionViewSet, InstitutionCreateView
from main.views.views import InstitutionListView
from main.views.views import InstitutionDetailView, RefNumberDetailView, DocumentDetailView, DocumentHistoryView
from main.views.views_upload_old import AddInstitutionView, AddRefNumberView, AddDocumentView
from main.views.views_upload_old import batch_upload, load_ref_numbers
from main.views.views_upload_old import EditMetaView, EditTranscriptView
from main.views.views_upload_old import thanks_view
from main.views.views_user import signup, userprofile, UserUpdateView
from main.views.views_user import CustomLoginView
from main.views.views_user import activate, AccountActivationSentView
from main.views.views_user import CustomPasswordConfirmView, CustomPasswordResetView, CustomPasswordChangeView
from main.views.views_export import DocumentExportView
import main.views.views_upload as v_upload
import main.views.views_admin as views_admin
import main.views.views_search as v_search
import main.views.views_autocomplete as v_autocomplete

router = DefaultRouter()
router.register('institutions', InstitutionViewSet)


app_name = 'main'
urlpatterns = [
    # ADMIN PAGES
    path('transcriptiones_admin/', views_admin.admin_view, name='admin'),
    path('transcriptiones_admin/statistics/', views_admin.admin_statistics_view, name='admin_statistics'),
    path('transcriptiones_admin/merge_doc/', views_admin.admin_merge_docs_view, name='admin_merge_docs'),
    path('transcriptiones_admin/export/json/', views_admin.admin_export_json_view, name='admin_export_json'),

    path('search_test/', v_search.test_search, name='search_test'),
    path('test/', test, name='test'),
    path('test_dd/', test_dropdown, name='test_dd'),
    path('test_modals/', test_bsmodals2, name='test_modals'),
    path('dummy/', test, name='dummy'),
    path('api/', include(router.urls)),
    path('create_institution/', InstitutionCreateView.as_view(), name='create_institution'),

    path('insti_idx/', v_upload.new_index_inst, name='index_inst'),
    path('instis/create/', v_upload.InstCreateView.as_view(), name='create_inst'),
    path('instis/', v_upload.insts, name='insts'),

    # Autocomplete Views for upload form
    url(r'^inst-autocomplete/$', v_autocomplete.InstitutionAutocomplete.as_view(), name='inst-autocomplete', ),
    url(r'^refn-autocomplete/$', v_autocomplete.RefNumberAutocomplete.as_view(), name='refn-autocomplete', ),
    url(r'^srctype-autocomplete/$', v_autocomplete.SourceTypeAutocomplete.as_view(), name='srctype-autocomplete', ),
    url(r'^srctype-ch-autocomplete/$', v_autocomplete.SourceTypeChildAutocomplete.as_view(), name='srctype-ch-autocomplete', ),
    url(r'^author-autocomplete/$', v_autocomplete.AuthorAutocomplete.as_view(), name='author-autocomplete', ),
    url(r'^language-autocomplete/$', v_autocomplete.LanguageAutocomplete.as_view(), name='language-autocomplete', ),

    # auto complete views
    # path('ac-institution', InstitutionAutocomplete.as_view(create_field='institution_name'), name='ac-institution'),
    # path('ac-ref_number', RefNumberAutocomplete.as_view(create_field='ref_number_name'), name='ac-ref_number'),

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

    path('display/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/<int:version_nr>/', DocumentDetailView.as_view(),
         name='document_legacy_detail'),
    path('display/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/history/', DocumentHistoryView.as_view(),
         name='document_history'),
    path('display/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/export/', DocumentExportView.as_view(),
         name='document_export'),

    # urls for upload views
    path('upload/', v_upload.new_index_inst, name='upload_document'),
    path('upload/addinstitution/', AddInstitutionView.as_view(), name='institution_add'),
    path('upload/addrefnumber/', AddRefNumberView.as_view(), name='ref_number_add'),
    path('upload/ajax/load-refnumbers/', load_ref_numbers, name='ajax_load_ref_numbers'),
    path('upload/thanks/', thanks_view, name='thanks'),
    path('upload/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/editmeta/', EditMetaView.as_view(), name='edit_meta'),
    path('upload/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/edittranscript/', EditTranscriptView.as_view(),
         name='edit_transcript'),
    path('upload/batch/', batch_upload, name='batch_upload'),

    # urls for search views
    path('search/', v_search.SearchView.as_view(), name='search'),

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

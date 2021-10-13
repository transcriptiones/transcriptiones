from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView, PasswordResetDoneView,\
    PasswordResetCompleteView
from main.views.views_upload_old import batch_upload
import main.views.views_admin as v_admin
import main.views.views_autocomplete as v_autocomplete
import main.views.views_browse as v_browse
import main.views.views_edit as v_edit
import main.views.views_export as v_export
import main.views.views_info as v_info
import main.views.views_messages as v_messages
import main.views.views_search as v_search
import main.views.views_subscriptions as v_subscriptions
import main.views.views_upload as v_upload
import main.views.views_user as v_user


app_name = 'main'
urlpatterns = [
    # ROOT VIEW
    path('', TemplateView.as_view(template_name='main/info/start.html'), name='start'),

    ##############
    # INFO PAGES
    path('info/guidelines/', TemplateView.as_view(template_name='main/info/guidelines.html'), name='guidelines'),
    path('info/tos/',        TemplateView.as_view(template_name='main/info/tos.html'),        name='tos'),
    path('info/about/',      TemplateView.as_view(template_name='main/info/about.html'),      name='about'),
    path('info/contact/', v_info.contact_view, name='contact'),

    ##############
    # SEARCH VIEW
    # path('search/', v_search.SearchView.as_view(), name='search'),
    path('search/', v_search.test_search_2, name='search'),
    path('search_box/<str:query>/', v_search.search_by_box_view, name='search_by_box'),
    path('search_redirect/', v_search.search_box_redirect, name='search_redirect'),

    ##############
    # UPLOAD PAGES
    path('upload/options/', v_upload.upload_options, name='upload_options'),
    # Upload form for a new document
    path('upload/document/', v_upload.upload_transcription_view, name='upload_document'),
    # Upload form for a new document
    path('upload/documents/', v_upload.upload_multiple_transcriptions_view, name='upload_multiple'),
    # Contact form for a batch upload
    path('upload/batch/', v_upload.upload_batch_view, name='upload_batch'),
    # Thank you screen after uploading
    path('upload/thanks/<int:doc_id>', v_upload.thanks_view, name='thank_you'),

    ##############
    # AUTOMPLETE VIEWS
    url(r'^inst-autocomplete/$', v_autocomplete.InstitutionAutocomplete.as_view(), name='inst-autocomplete', ),
    url(r'^refn-autocomplete/$', v_autocomplete.RefNumberAutocomplete.as_view(), name='refn-autocomplete', ),
    url(r'^srctype-autocomplete/$', v_autocomplete.SourceTypeAutocomplete.as_view(), name='srctype-autocomplete', ),
    url(r'^srctype-ch-autocomplete/$', v_autocomplete.SourceTypeChildAutocomplete.as_view(), name='srctype-ch-autocomplete', ),
    url(r'^author-autocomplete/$', v_autocomplete.AuthorAutocomplete.as_view(create_field='author_name'), name='author-autocomplete', ),
    url(r'^language-autocomplete/$', v_autocomplete.LanguageAutocomplete.as_view(), name='language-autocomplete', ),


    ##############
    # VIEW DATA PAGES
    path('display/', v_browse.InstitutionListView.as_view(), name='institution_list'),

    path('display/institutions/', v_browse.browse_options, name='browse_options'),
    path('display/institutions/<slug:inst_slug>/', v_browse.InstitutionDetailView.as_view(), name='institution_detail'),
    path('display/institutions/<slug:inst_slug>/<slug:ref_slug>/', v_browse.RefNumberDetailView.as_view(), name='ref_number_detail'),
    path('display/institutions/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/', v_browse.DocumentDetailView.as_view(), name='document_detail'),
    path('display/institutions/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/<int:version_nr>/', v_browse.DocumentDetailView.as_view(), name='document_legacy_detail'),
    path('display/institutions/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/history/', v_browse.DocumentHistoryView.as_view(), name='document_history'),
    path('display/institutions/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/export/', v_export.DocumentExportView.as_view(), name='document_export'),

    path('display/source_types/', v_browse.source_type_list_view, name='source_type_list'),
    path('display/source_types/<int:pk>/', v_browse.source_type_detail_view, name='source_type_detail'),
    path('display/source_types/<int:pk>/all/', v_browse.source_type_group_detail_view, name='source_type_group_detail'),

    path('display/authors/', v_browse.AuthorListView.as_view(), name='author_list'),
    path('display/authors/<int:pk>/', v_browse.AuthorDetailView.as_view(), name='author_detail'),

    path('insti_idx/', v_upload.upload_transcription_view, name='index_inst'),
    path('instis/create/', v_upload.ModalCreateInstitutionView.as_view(), name='create_inst'),
    path('refis/create/', v_upload.ModalCreateRefNumberView.as_view(), name='create_refn'),
    path('instis/', v_upload.institution_dropdown_view, name='insts'),
    path('refis/', v_upload.refnumber_dropdown_view, name='refns'),

    ##############
    # USER VIEWS
    path('user/signup/', v_user.signup, name='signup'),
    path('user/activationsent/', v_user.AccountActivationSentView.as_view(), name='account_activation_sent'),
    path('user/activate/<uidb64>/<token>/', v_user.activate, name='activate'),
    path('user/login/', v_user.CustomLoginView.as_view(), name='login'),
    path('user/logout/', LogoutView.as_view(template_name='main/users/logout.html'), name='logout'),
    path('user/passwordchange/', v_user.CustomPasswordChangeView.as_view(), name='password_change'),
    path('user/passwordchange/done/', PasswordChangeDoneView.as_view(template_name='main/users/password_change_done.html'), name='password_change_done'),
    path('user/profile/', v_user.userprofile, name='profile'),
    path('user/documents/', v_user.my_documents, name='my_documents'),
    path('user/documents/created/', v_user.my_documents, name='my_own_documents'),
    path('user/documents/drafts/', v_user.my_documents, name='my_document_drafts'),
    path('user/public/profile/<str:username>/', v_user.public_profile, name='public_profile'),
    path('user/profile/update/', v_user.UserUpdateView.as_view(), name='user_update'),
    path('user/passwordreset/', v_user.CustomPasswordResetView.as_view(), name='password_reset'),
    path('user/passwordreset/done/', PasswordResetDoneView.as_view(template_name='main/users/password_reset_done.html'), name='password_reset_done'),
    path('user/reset/<uidb64>/<token>/', v_user.CustomPasswordConfirmView.as_view(), name='password_reset_confirm'),
    path('user/reset/done/', PasswordResetCompleteView.as_view(template_name='main/users/password_reset_complete.html'), name='password_reset_complete'),
    path('user/usernamerequest/', v_user.request_username_view, name='username_request'),
    path('user/usernamerequest/done', v_user.request_username_done_view, name='username_request_done'),

    ##############
    # USER SUBSCRIPTIONS
    path('user/subscriptions/', v_subscriptions.subscriptions, name='subscriptions'),
    path('subscribe/institution/<int:pk>/', v_subscriptions.subscribe_institution_view, name='subscribe_institution'),
    path('subscribe/ref_number/<int:pk>/', v_subscriptions.subscribe_ref_number_view, name='subscribe_ref_number'),
    path('subscribe/document/<int:pk>/', v_subscriptions.subscribe_document_view, name='subscribe_document'),
    path('subscribe/user/<int:pk>/', v_subscriptions.subscribe_user_view, name='subscribe_user'),
    path('subscribe/author/<int:pk>/', v_subscriptions.subscribe_author_view, name='subscribe_author'),
    path('unsubscribe/institution/<int:pk>/', v_subscriptions.unsubscribe_institution_view, name='unsubscribe_institution'),
    path('unsubscribe/ref_number/<int:pk>/', v_subscriptions.unsubscribe_ref_number_view, name='unsubscribe_ref_number'),
    path('unsubscribe/document/<int:pk>/', v_subscriptions.unsubscribe_document_view, name='unsubscribe_document'),
    path('unsubscribe/user/<int:pk>/', v_subscriptions.unsubscribe_user_view, name='unsubscribe_user'),
    path('unsubscribe/author/<int:pk>/', v_subscriptions.unsubscribe_author_view, name='unsubscribe_author'),
    path('unsubscribe/all/', v_subscriptions.unsubscribe_all_view, name='unsubscribe_all'),

    ##############
    # USER MESSAGES & NOTIFICATIONS
    path('user/messages/', v_messages.messages_view, name='messages'),
    path('user/messages/delete/all', v_messages.delete_all_messages_view, name='messages_delete_all'),
    path('user/messages/delete/<str:message_type>/<int:message_id>', v_messages.messages_delete_view, name='messages_delete'),
    path('user/messages/view/<str:message_type>/<int:message_id>/', v_messages.messages_read_view, name='messages_read'),
    path('user/messages/reply/<int:message_id>/', v_messages.messages_reply_view, name='messages_reply'),
    path('user/messages/unread/<str:message_type>/<int:message_id>/', v_messages.messages_mark_unread_view, name='messages_mark_unread'),
    path('user/messages/compose/', v_messages.message_user_view, name='write_message'),
    path('user/messages/compose/<str:username>/', v_messages.message_user_view, name='message_user'),

    ##############
    # ADMIN PAGES
    path('transcriptiones_admin/', v_admin.admin_view, name='admin'),
    path('transcriptiones_admin/inbox/', v_admin.admin_inbox_view, name='admin_inbox'),
    path('transcriptiones_admin/users/', v_admin.admin_users_view, name='admin_users'),
    path('transcriptiones_admin/expert/', v_admin.admin_expert_view, name='admin_expert'),
    path('transcriptiones_admin/statistics/', v_admin.admin_statistics_view, name='admin_statistics'),
    path('transcriptiones_admin/merge_doc/', v_admin.admin_merge_docs_view, name='admin_merge_docs'),
    path('transcriptiones_admin/export/json/', v_admin.admin_export_json_view, name='admin_export_json'),
    # ADMIN FUNCTIONS
    path('transcriptiones_admin/activate_user/<int:user_id>', v_admin.activate_user, name='admin_activate_user'),
    path('transcriptiones_admin/deactivate_user/<int:user_id>', v_admin.deactivate_user, name='admin_deactivate_user'),
    path('transcriptiones_admin/set_user_staff/<int:user_id>', v_admin.set_user_staff, name='admin_set_user_staff'),
    path('transcriptiones_admin/set_user_admin/<int:user_id>', v_admin.set_user_admin, name='admin_set_user_admin'),
    path('transcriptiones_admin/set_user_user/<int:user_id>', v_admin.set_user_user, name='admin_set_user_user'),

    path('upload/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/editmeta/', v_edit.edit_meta_view, name='edit_meta'),
    path('upload/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/edittranscript/', v_edit.edit_transcription_view, name='edit_transcript'),
    path('upload/batch/', batch_upload, name='batch_upload'),




    ]

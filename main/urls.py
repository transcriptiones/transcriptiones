from django.conf.urls import url
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView, PasswordResetDoneView,\
    PasswordResetCompleteView

import main.views.views_error
from main.views.views_upload_old import batch_upload
import main.views.views_admin as v_admin
import main.views.views_autocomplete as v_autocomplete
import main.views.views_browse as v_browse
import main.views.views_edit as v_edit
import main.views.views_export as v_export
import main.views.views_info as v_info
import main.views.views_messages as v_messages
import main.views.views_news as v_news
import main.views.views_search as v_search
import main.views.views_subscriptions as v_subscriptions
import main.views.views_upload as v_upload
import main.views.views_user as v_user
import main.views.views_api as v_api


app_name = 'main'
urlpatterns = [
    # ROOT VIEW
    path('', v_info.start_view, name='start'),
    path('set_language/<str:language>/', v_info.set_language_view, name='set_tr_language'),

    ##############
    # INFO PAGES
    path('info/', TemplateView.as_view(template_name='main/info/blank.html'), name='info'),
    path('info/instructions/', v_info.guidelines_view, name='guidelines'),
    path('info/tos/',        TemplateView.as_view(template_name='main/info/tos.html'),        name='tos'),
    path('info/about/',      TemplateView.as_view(template_name='main/info/about.html'),      name='about'),
    path('info/contact/', v_info.contact_view, name='contact'),
    path('info/faq/', TemplateView.as_view(template_name='main/info/faq.html'), name='faq'),
    path('info/unsubscribe/', v_info.unsubsribe_newsletter_view, name='unsubscribe_newsletter'),

    ##############
    # SEARCH VIEW
    # path('search/', v_search.SearchView.as_view(), name='search'),
    path('search/', v_search.transcriptiones_search, name='search'),
    path('search_redirect/', v_search.search_box_redirect, name='search_redirect'),

    ##############
    # News VIEW
    path('news/', v_news.news_view, name='news'),

    ##############
    # UPLOAD PAGES
    path('upload/options/', v_upload.upload_options, name='upload_options'),
    # Upload form for a new document
    path('upload/document/', v_upload.upload_transcription_view, name='upload_document'),
    # Upload form for a new document
    # path('upload/documents/', v_upload.upload_multiple_transcriptions_view, name='upload_multiple'),
    # Contact form for a batch upload
    path('upload/batch/', v_upload.upload_batch_view, name='upload_batch'),
    # Thank you screen after uploading
    path('upload/thanks/<int:doc_id>', v_upload.thanks_view, name='thank_you'),

    ##############
    # AUTOCOMPLETE VIEWS
    url(r'^inst-autocomplete/$', v_autocomplete.InstitutionAutocomplete.as_view(), name='inst-autocomplete', ),
    path('inst-autocomplete-id/', v_autocomplete.institution_id_view, name='inst-autocomplete-id', ),
    url(r'^refn-autocomplete/$', v_autocomplete.RefNumberAutocomplete.as_view(), name='refn-autocomplete', ),
    path('refn-autocomplete-id/', v_autocomplete.refnumber_id_view, name='refn-autocomplete-id', ),
    url(r'^srctype-autocomplete/$', v_autocomplete.SourceTypeAutocomplete.as_view(), name='srctype-autocomplete', ),
    url(r'^srctype-ch-autocomplete/$', v_autocomplete.SourceTypeChildAutocomplete.as_view(), name='srctype-ch-autocomplete', ),
    url(r'^author-autocomplete/$', v_autocomplete.AuthorAutocomplete.as_view(create_field='author_name'), name='author-autocomplete', ),
    url(r'^language-autocomplete/$', v_autocomplete.LanguageAutocomplete.as_view(), name='language-autocomplete', ),

    ##############
    # VIEW DATA PAGES
    path('display/', v_browse.browse_options, name='browse_options'),

    path('display/institutions/', v_browse.InstitutionListView.as_view(), name='institution_list'),
    path('display/institutions/<slug:inst_slug>/', v_browse.InstitutionDetailView.as_view(), name='institution_detail'),
    path('display/institutions/<slug:inst_slug>/<slug:ref_slug>/', v_browse.RefNumberDetailView.as_view(), name='ref_number_detail'),
    path('display/institutions/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/', v_browse.DocumentDetailView.as_view(), name='document_detail'),
    path('display/institutions/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/<int:version_nr>/', v_browse.DocumentDetailView.as_view(), name='document_legacy_detail'),
    path('display/institutions/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/history/', v_browse.DocumentHistoryView.as_view(), name='document_history'),
    path('display/institutions/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/export/', v_export.DocumentExportView.as_view(), name='document_export'),

    path('display/source_types/', v_browse.source_type_list_view, name='source_type_list'),
    path('display/source_types/<int:pk>/', v_browse.source_type_detail_view, name='source_type_detail'),
    path('display/source_types/<int:pk>/all/', v_browse.source_type_group_detail_view, name='source_type_group_detail'),

    path('display/scribes/', v_browse.AuthorListView.as_view(), name='author_list'),
    path('display/scribes/<int:pk>/', v_browse.AuthorDetailView.as_view(), name='author_detail'),

    path('insti_idx/', v_upload.upload_transcription_view, name='index_inst'),
    path('instis/create/', v_upload.ModalCreateInstitutionView.as_view(), name='create_inst'),
    path('refis/create/', v_upload.ModalCreateRefNumberView.as_view(), name='create_refn'),
    path('instis/', v_upload.institution_dropdown_view, name='insts'),
    path('refis/', v_upload.refnumber_dropdown_view, name='refns'),

    ##############
    # USER VIEWS
    path('user/signup/', v_user.signup, name='signup'),
    path('user/activationsent/', v_user.AccountActivationSentView.as_view(), name='account_activation_sent'),
    path('user/activate/<uidb64>/<token>/', v_user.show_activation_page, name='activate'),
    path('user/activate/', v_user.activate, name='activate_user'),
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
    path('user/profile/email_update/', v_user.change_email_view, name='user_email_update'),
    path('user/passwordreset/', v_user.CustomPasswordResetView.as_view(), name='password_reset'),
    path('user/passwordreset/done/', PasswordResetDoneView.as_view(template_name='main/users/password_reset_done.html'), name='password_reset_done'),
    path('user/reset/<uidb64>/<token>/', v_user.CustomPasswordConfirmView.as_view(), name='password_reset_confirm'),
    path('user/reset/done/', PasswordResetCompleteView.as_view(template_name='main/users/password_reset_complete.html'), name='password_reset_complete'),
    path('user/usernamerequest/', v_user.request_username_view, name='username_request'),
    path('user/usernamerequest/done', v_user.request_username_done_view, name='username_request_done'),
    path('user/emailchange/done', v_user.request_email_change_done_view, name='change_email_request_done'),

    ##############
    # USER SUBSCRIPTIONS
    path('user/subscriptions/', v_subscriptions.subscriptions, name='subscriptions'),
    path('subscribe/institution/<int:pk>/', v_subscriptions.subscribe_institution_view, name='subscribe_institution'),
    path('subscribe/ref_number/<int:pk>/', v_subscriptions.subscribe_ref_number_view, name='subscribe_ref_number'),
    path('subscribe/document/<int:pk>/', v_subscriptions.subscribe_document_view, name='subscribe_document'),
    path('subscribe/user/<int:pk>/', v_subscriptions.subscribe_user_view, name='subscribe_user'),
    path('subscribe/scribe/<int:pk>/', v_subscriptions.subscribe_author_view, name='subscribe_author'),
    path('unsubscribe/institution/<int:pk>/', v_subscriptions.unsubscribe_institution_view, name='unsubscribe_institution'),
    path('unsubscribe/ref_number/<int:pk>/', v_subscriptions.unsubscribe_ref_number_view, name='unsubscribe_ref_number'),
    path('unsubscribe/document/<int:pk>/', v_subscriptions.unsubscribe_document_view, name='unsubscribe_document'),
    path('unsubscribe/user/<int:pk>/', v_subscriptions.unsubscribe_user_view, name='unsubscribe_user'),
    path('unsubscribe/scribe/<int:pk>/', v_subscriptions.unsubscribe_author_view, name='unsubscribe_author'),
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
    path('transcriptiones_admin/', v_admin.admin_view, name='admin_start'),
    path('transcriptiones_admin/inbox/', v_admin.admin_inbox_view, name='admin_inbox'),
    path('transcriptiones_admin/inbox/<int:msg_id>/', v_admin.admin_inbox_message_view, name='admin_inbox_message'),
    path('transcriptiones_admin/inbox/<int:msg_id>/delete/', v_admin.admin_inbox_message_delete, name='admin_inbox_message_delete'),
    path('transcriptiones_admin/inbox/<int:msg_id>/answer/', v_admin.admin_inbox_message_answer, name='admin_inbox_message_answer'),
    path('transcriptiones_admin/inbox/<int:msg_id>/mark_answered/', v_admin.admin_inbox_message_mark_answered, name='admin_inbox_message_mark_answered'),
    path('transcriptiones_admin/inbox/<int:msg_id>/mark_spam/', v_admin.admin_inbox_message_mark_spam, name='admin_inbox_message_mark_spam'),
    path('transcriptiones_admin/inbox/<int:msg_id>/mark_read/', v_admin.admin_inbox_message_mark_read, name='admin_inbox_message_mark_read'),
    path('transcriptiones_admin/inbox/<int:msg_id>/mark_unread/', v_admin.admin_inbox_message_mark_unread, name='admin_inbox_message_mark_unread'),
    path('transcriptiones_admin/users/', v_admin.admin_users_view, name='admin_users'),
    path('transcriptiones_admin/statistics/', v_admin.admin_statistics_view, name='admin_statistics'),
    path('transcriptiones_admin/merge_doc/', v_admin.admin_merge_docs_view, name='admin_merge_docs'),
    path('transcriptiones_admin/export/json/', v_admin.admin_export_json_view, name='admin_export_json'),
    path('transcriptiones_admin/send_newsletter/', v_admin.send_newsletter_view, name='admin_send_newsletter'),

    # ADMIN FUNCTIONS
    path('transcriptiones_admin/activate_user/<int:user_id>', v_admin.activate_user, name='admin_activate_user'),
    path('transcriptiones_admin/deactivate_user/<int:user_id>', v_admin.deactivate_user, name='admin_deactivate_user'),
    path('transcriptiones_admin/set_user_staff/<int:user_id>', v_admin.set_user_staff, name='admin_set_user_staff'),
    path('transcriptiones_admin/set_user_admin/<int:user_id>', v_admin.set_user_admin, name='admin_set_user_admin'),
    path('transcriptiones_admin/set_user_user/<int:user_id>', v_admin.set_user_user, name='admin_set_user_user'),

    path('upload/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/editmetadata/', v_edit.edit_meta_view, name='edit_meta'),
    path('upload/<slug:inst_slug>/<slug:ref_slug>/<slug:doc_slug>/edittranscription/', v_edit.edit_transcription_view, name='edit_transcript'),
    path('upload/batch/', batch_upload, name='batch_upload'),

    ##############
    # TRANSCRIPTIONES API
    path('api/documentation/', v_api.api_doc_view, name='api_doc_view'),
    path('api/<str:api_version>/<str:api_request>/', v_api.api_view, name='api_view'),
    path('api/<str:api_version>/<str:api_request>/<int:object_id>/', v_api.api_detail_view, name='api_detail_view'),
    path('api/<str:api_version>/documents/<int:object_id>/tei/', v_api.api_tei_export_view, name='api_tei_export'),
    path('api/<str:api_version>/documents/<int:object_id>/plain/', v_api.api_plain_export_view, name='api_plain_export'),
    path('user/request_api_key/', v_user.generate_api_secret, name='api_request'),
    path('user/renew_api_key/', v_user.renew_api_secret, name='api_renew'),
    path('user/delete_api_key/', v_user.delete_api_secret, name='api_delete'),

    path('document/transcription/<int:doc_id>/', v_browse.transcription_view, name='transcription_iframe'),

    #############
    # DEBUG VIEWS
    path('debug/400', main.views.views_error.custom_bad_request_view, name='bad_request'),
    path('debug/403', main.views.views_error.custom_permission_denied_view, name='permission_denied'),
    path('debug/404', main.views.views_error.custom_page_not_found_view, name='page_not_found'),
    path('debug/500', main.views.views_error.custom_error_view, name='server_error'),
    ]

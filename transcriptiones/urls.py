"""transcriptiones URL Configuration
1. '' points to the main transcriptiones web app
2. 'admin' points to the Django administration interface
3. 'i18n' points to the language selection views

"""
from django.contrib import admin
from django.urls import include, path

handler404 = 'main.views.views_error.custom_page_not_found_view'
handler500 = 'main.views.views_error.custom_error_view'
handler403 = 'main.views.views_error.custom_permission_denied_view'
handler400 = 'main.views.views_error.custom_bad_request_view'

urlpatterns = [
    path('',  include('main.urls')),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('captcha/', include('captcha.urls')),
    ]

"""transcriptiones URL Configuration
1. '' points to the main transcriptiones web app
2. 'admin' points to the Django administration interface
3. 'i18n' points to the language selection views

"""
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('',  include('main.urls')),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    ]

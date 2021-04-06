from django.urls import path
from django.views.generic import TemplateView

from .views import views, infoviews

app_name = 'main'
urlpatterns = [
    path('', views.dummy, name='dummy'),

    # urls for info views
    path('', infoviews.StartView.as_view(), name='start'),
    path('info/guidelines/', TemplateView.as_view(template_name='info/guidelines.html'), name='guidelines'),
    path('info/tos/',        TemplateView.as_view(template_name='info/tos.html'),        name='tos'),
    path('info/about/',      TemplateView.as_view(template_name='info/about.html'),      name='about'),
    path('info/aboutus/',    TemplateView.as_view(template_name='info/aboutus.html'),    name='aboutus'),
    path('info/contact/',    TemplateView.as_view(template_name='info/contact.html'),    name='contact'),
    ]

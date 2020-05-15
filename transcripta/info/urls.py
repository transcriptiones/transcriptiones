from django.urls import path
from transcripta.info.views import StartView

urlpatterns = [
    path('', StartView.as_view(), name = "start")
    ]
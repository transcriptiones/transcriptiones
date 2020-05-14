from django.urls import path
from transcripta.transkriptionen.views import InstitutionListView, InstitutionDetailView, RefNumberDetailView, DocumentTitleDetailView

urlpatterns = [
     #so ist die URL noch irreführend. .../transkriptionen aber man kommt auf eine Liste mit Institutionen
    path('', InstitutionListView.as_view(), name = 'institutionlist'),
    path('<slug:instslug>/', InstitutionDetailView.as_view(), name = 'institutiondetail'),
    path('<slug:instslug>/<slug:refslug>/', RefNumberDetailView.as_view(), name = 'refnumberdetail'),
    path('<slug:instslug>/<slug:refslug>/<slug:docslug>/', DocumentTitleDetailView.as_view(), name='documenttitledetail')
    ]
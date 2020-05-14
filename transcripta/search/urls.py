from django.urls import path
from transcripta.search.views import SearchView, ResultsView

urlpatterns = [
    path('', SearchView.as_view(), name = 'searchform'),
    path('results/', ResultsView.as_view(), name='searchresults')
    ]

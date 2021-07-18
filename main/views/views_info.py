from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView
from django_tables2 import MultiTableMixin, SingleTableMixin
from django_filters.views import FilterView

import main.model_info as m_info
from main.forms.forms_info import ContactForm
from main.models import Institution, RefNumber, Document, UserSubscription
from main.tables import TitleValueTable, RefNumberTable, DocumentTable, InstitutionTable
from main.filters import InstitutionFilter, RefNumberFilter, DocumentFilter


def contact_view(request):
    form = ContactForm()
    return render(request, 'main/info/contact.html', context={'form': form})

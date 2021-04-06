from django.shortcuts import render
from django.http.response import HttpResponse
from django.utils.translation import ugettext as _


def dummy(request):
    # return HttpResponse(_('Test'))
    return render(request, 'main/dummy.html')

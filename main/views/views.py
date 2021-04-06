from django.shortcuts import render
from django.http.response import HttpResponse
from django.utils.translation import ugettext as _


def test(request):
    # return HttpResponse(_('Test'))
    return render(request, 'main/test.html')

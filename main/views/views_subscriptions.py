from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


@login_required
def subscribe_ref_number_view(request, pk):

    return HttpResponse("niy")


@login_required
def subscribe_document_view(request, pk):
    return HttpResponse("niy")


@login_required
def subscribe_user_view(request, pk):
    return HttpResponse("niy")


@login_required
def unsubscribe_ref_number_view(request, pk):
    return HttpResponse("niy")


@login_required
def unsubscribe_document_view(request, pk):
    return HttpResponse("niy")


@login_required
def unsubscribe_user_view(request, pk):
    return HttpResponse("niy")


@login_required
def unsubscribe_all_view(request):
    return HttpResponse("niy")

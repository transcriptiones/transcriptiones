from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from main.models import Document, RefNumber, User, UserSubscription


@login_required
def subscriptions(request):
    return HttpResponse("niy")


@login_required
def subscribe_ref_number_view(request, pk):
    try:
        ref_number = RefNumber.objects.get(pk=pk)
        UserSubscription.objects.create(user=request.user,
                                        subscription_type=UserSubscription.SubscriptionType.REF_NUMBER,
                                        object_id=ref_number.id)
        messages.success(request, _('Subscription added'))
    except RefNumber.DoesNotExist:
        messages.error(request, _('Could not add subscription'))

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def subscribe_document_view(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except RefNumber.DoesNotExist:
        document = None

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

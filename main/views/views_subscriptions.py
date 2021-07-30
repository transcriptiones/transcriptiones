from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from main.forms.forms_user import UserSubscriptionOptionsForm
from main.tables.tables import UserSubscriptionTable
from main.models import Document, RefNumber, User, UserSubscription, Author


@login_required
def subscriptions(request):
    table = UserSubscriptionTable(data=UserSubscription.objects.filter(user=request.user))
    form = UserSubscriptionOptionsForm()

    if request.method == 'POST':
        form = UserSubscriptionOptionsForm(request.POST)

    return render(request, 'main/users/subscriptions.html', {'table': table, 'form': form})


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
        UserSubscription.objects.create(user=request.user,
                                        subscription_type=UserSubscription.SubscriptionType.DOCUMENT,
                                        object_id=document.id)
        messages.success(request, _('Subscription added'))
    except Document.DoesNotExist:
        messages.error(request, _('Could not add subscription'))

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def subscribe_user_view(request, pk):
    try:
        user = User.objects.get(pk=pk)
        UserSubscription.objects.create(user=request.user,
                                        subscription_type=UserSubscription.SubscriptionType.USER,
                                        object_id=user.id)
        messages.success(request, _('Subscription added'))
    except User.DoesNotExist:
        messages.error(request, _('Could not add subscription'))

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def subscribe_author_view(request, pk):
    try:
        author = Author.objects.get(pk=pk)
        UserSubscription.objects.create(user=request.user,
                                        subscription_type=UserSubscription.SubscriptionType.AUTHOR,
                                        object_id=author.id)
        messages.success(request, _('Subscription added'))
    except User.DoesNotExist:
        messages.error(request, _('Could not add subscription'))

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def unsubscribe_ref_number_view(request, pk):
    return do_unsubscribe(request, pk, UserSubscription.SubscriptionType.REF_NUMBER)


@login_required
def unsubscribe_document_view(request, pk):
    return do_unsubscribe(request, pk, UserSubscription.SubscriptionType.DOCUMENT)


@login_required
def unsubscribe_user_view(request, pk):
    return do_unsubscribe(request, pk, UserSubscription.SubscriptionType.USER)


@login_required
def unsubscribe_author_view(request, pk):
    return do_unsubscribe(request, pk, UserSubscription.SubscriptionType.AUTHOR)


def do_unsubscribe(request, pk, sub_type):
    try:
        sub = UserSubscription.objects.get(user=request.user, subscription_type=sub_type, object_id=pk)
        sub.delete()
        messages.success(request, _('Subscription removed'))
    except UserSubscription.DoesNotExist:
        messages.error(request, _('Could not remove subscription'))

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def unsubscribe_all_view(request):
    try:
        subs = UserSubscription.objects.filter(user=request.user)
        for sub in subs:
            sub.delete()
        messages.success(request, _('Subscription removed'))
    except UserSubscription.DoesNotExist:
        messages.error(request, _('Could not remove subscription'))

    return redirect(request.META.get('HTTP_REFERER'))

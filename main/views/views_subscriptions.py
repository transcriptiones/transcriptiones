from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _

from main.forms.forms_user import UserSubscriptionOptionsForm
from main.tables.tables import UserSubscriptionTable
from main.models import Document, RefNumber, User, UserSubscription, Author, Institution


@login_required
def subscriptions(request):
    subs = UserSubscription.objects.filter(user=request.user)
    table = UserSubscriptionTable(data=subs)
    form = UserSubscriptionOptionsForm({'notification_policy': request.user.notification_policy,
                                        'different_editor_subscription': request.user.different_editor_subscription})

    if request.method == 'POST':
        form = UserSubscriptionOptionsForm(request.POST)
        if form.is_valid():
            request.user.notification_policy = form.cleaned_data["notification_policy"]
            request.user.different_editor_subscription = form.cleaned_data["different_editor_subscription"]
            request.user.save()
            messages.success(request, _("Your Subscription Options have been updated"))

    return render(request, 'main/users/subscriptions.html', {'table': table, 'form': form})


@login_required
def subscribe_institution_view(request, pk):
    try:
        institution = Institution.objects.get(pk=pk)
        UserSubscription.objects.create(user=request.user,
                                        subscription_type=UserSubscription.SubscriptionType.INSTITUTION,
                                        object_id=institution.id)
        messages.success(request, _('Subscription added'))
    except Institution.DoesNotExist:
        messages.error(request, _('Could not add subscription'))

    return redirect(request.META.get('HTTP_REFERER'))


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
        document = Document.all_objects.get(pk=pk).get_versions().latest()
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
def unsubscribe_institution_view(request, pk):
    return do_unsubscribe(request, pk, UserSubscription.SubscriptionType.INSTITUTION)


@login_required
def unsubscribe_ref_number_view(request, pk):
    return do_unsubscribe(request, pk, UserSubscription.SubscriptionType.REF_NUMBER)


@login_required
def unsubscribe_document_view(request, pk):
    latest_version_id = Document.all_objects.get(id=pk).get_versions().latest().id
    return do_unsubscribe(request, latest_version_id, UserSubscription.SubscriptionType.DOCUMENT)


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
        messages.success(request, _('All subscriptions removed'))
    except UserSubscription.DoesNotExist:
        messages.error(request, _('Could not remove subscriptions'))

    return redirect(request.META.get('HTTP_REFERER'))

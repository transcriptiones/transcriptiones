from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _

from main.forms.forms_user import UserMessageOptionsForm, WriteMessageForm, UserSubscriptionOptionsForm
from main.tables.tables import UserMessageTable, UserNotificationTable
from main.models import User, UserMessage, UserNotification


@login_required
def messages_view(request):
    table = UserMessageTable(data=UserMessage.objects.filter(receiving_user=request.user).order_by('-sending_time'))
    form = UserMessageOptionsForm()

    if request.method == 'POST':
        form = UserMessageOptionsForm(request.POST)

    return render(request, 'main/users/messages.html', {'table': table, 'form': form})


@login_required
def messages_read_view(request, message_id):
    try:
        message = UserMessage.objects.get(id=message_id, receiving_user=request.user)
    except UserMessage.DoesNotExist:
        messages.error(request, _('This message does not exist or does not belong to you.'))
        return HttpResponseRedirect('main:messages')

    message.viewing_state = 1
    message.save()

    return render(request, 'main/users/read_message.html', {'message': message})


@login_required
def message_user_view(request, username, subject='', message=''):
    receiving_user = User.objects.get(username=username)
    form = WriteMessageForm(user=receiving_user, subject=subject, message=message)

    if request.method == "POST":
        form = WriteMessageForm(request.POST, user=receiving_user)
        if form.is_valid():
            new_message = UserMessage.objects.create(sending_user=request.user,
                                                     receiving_user=receiving_user,
                                                     subject=form.cleaned_data['subject'],
                                                     message=form.cleaned_data['message'])
            messages.success(request, _('Your message has been sent.'))
            return redirect('main:messages')

    return render(request, 'main/users/write_message.html', {'form': form})


@login_required
def messages_reply_view(request, message_id):
    try:
        message = UserMessage.objects.get(id=message_id, receiving_user=request.user)
    except UserMessage.DoesNotExist:
        messages.error(request, _('This message does not exist or does not belong to you.'))
        return HttpResponseRedirect('main:messages')

    reply_message = f"\n\n\nOn {message.sending_time}, {message.sending_user.username} wrote:\n"
    message_lines = message.message.split("\n")
    for line in message_lines:
        reply_message += ">> " + line + "\n"

    return message_user_view(request, message.sending_user.username, subject='Re: '+message.subject, message=reply_message)


@login_required
def messages_delete_view(request, message_id):
    try:
        message = UserMessage.objects.get(id=message_id, receiving_user=request.user)
    except UserMessage.DoesNotExist:
        messages.error(request, _('This message does not exist or does not belong to you.'))
        return HttpResponseRedirect('main:messages')

    message.delete()
    messages.success(request, _('The message has been deleted.'))
    return redirect('main:messages')


@login_required
def notifications_view(request):
    table = UserNotificationTable(data=UserNotification.objects.filter(user=request.user))
    form = UserSubscriptionOptionsForm()

    if request.method == 'POST':
        form = UserSubscriptionOptionsForm(request.POST)

    return render(request, 'main/users/notifications.html', {'table': table, 'form': form})


@login_required
def notifications_read_view(request, notification_id):
    try:
        notification = UserNotification.objects.get(id=notification_id, user=request.user)
    except UserMessage.DoesNotExist:
        messages.error(request, _('This notification does not exist or does not belong to you.'))
        return HttpResponseRedirect('main:notifications')

    notification.viewing_state = 1
    notification.save()

    return render(request, 'main/users/read_notification.html', {'notification': notification})


@login_required
def notifications_delete_view(request, notification_id):
    try:
        notification = UserNotification.objects.get(id=notification_id, user=request.user)
    except UserNotification.DoesNotExist:
        messages.error(request, _('This notification does not exist or does not belong to you.'))
        return HttpResponseRedirect('main:notifications')

    notification.delete()
    messages.success(request, _('The notification has been deleted.'))
    return HttpResponseRedirect('main:notifications')


@login_required
def delete_all_messages_view(request):
    the_messages = UserMessage.objects.filter(receiving_user=request.user)
    for a_message in the_messages:
        a_message.delete()
    messages.success(_('All messages have been deleted.'))
    return redirect('main:messages')


@login_required
def delete_all_notifications_view(request):
    return HttpResponse('NIY')


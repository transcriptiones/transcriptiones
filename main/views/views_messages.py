from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from main.mail_utils import send_user_message_mail
from main.forms.forms_user import UserMessageOptionsForm
from main.tables.tables import UserMessageTable
from main.models import User, UserNotification


@login_required
def messages_view(request):
    """Shows the user message inbox and a form to set the message notification policy. In the model there are two
    kinds of messages: the Notifications (result of a subscribed object changing) and the Messages (messages from
    other users or the system). This view shows a table with those combined."""
    user_message_data = list()
    user_notifications = UserNotification.objects.filter(user=request.user).order_by('-sending_time')

    for notif in user_notifications:
        user_message_data.append({'message_type': 'notification',
                                  'pk': notif.id,
                                  'viewing_state': notif.viewing_state,
                                  'sending_user': 'transcriptiones',
                                  'subject': notif.subject,
                                  'sending_time': notif.sending_time})

    user_message_data = sorted(user_message_data, key=lambda d: d['sending_time'], reverse=True)
    table = UserMessageTable(data=user_message_data)
    form = UserMessageOptionsForm({'message_notification_policy': request.user.message_notification_policy})

    if request.method == 'POST':
        form = UserMessageOptionsForm(request.POST)
        if form.is_valid():
            request.user.message_notification_policy = form.cleaned_data['message_notification_policy']
            request.user.save()
            messages.success(request, _('Your notification policy has been updated.'))

    return render(request, 'main/users/messages.html', {'table': table, 'form': form})


@login_required
def messages_read_view(request, message_type, message_id):
    """Shows a message or notification to read. The template provides options to delete the message or mark it as
    unread. A message can be of the message_type 'message' or 'notification'. """
    message = get_message(message_type, message_id, request.user)

    if message is None:
        messages.error(request, _('This message does not exist or does not belong to you.'))
        return reverse('main:messages')

    message.viewing_state = 1
    message.save()

    return render(request, 'main/users/read_message.html', {'message_type': message_type, 'message': message})


@login_required
def messages_mark_unread_view(request, message_type, message_id):
    message = get_message(message_type, message_id, request.user)
    if message is None:
        messages.error(request, _('This message does not exist or does not belong to you.'))
        return HttpResponseRedirect(reverse('main:messages'))

    message.viewing_state = 0
    message.save()
    return HttpResponseRedirect(reverse('main:messages'))


@login_required
def messages_delete_view(request, message_type, message_id):
    """Deletes a single message/notification of the current user."""
    message = get_message(message_type, message_id, request.user)

    if message is None:
        messages.error(request, _('This message does not exist or does not belong to you.'))
        return redirect('main:messages')

    message.delete()
    messages.success(request, _('The message has been deleted.'))
    return redirect('main:messages')


@login_required
def delete_all_messages_view(request):
    """Deletes all the messages/notifications of the current user."""
    the_notifications = UserNotification.objects.filter(user=request.user)
    for a_notification in the_notifications:
        a_notification.delete()

    messages.success(request, _('All messages have been deleted.'))
    return redirect('main:messages')


def get_message(message_type, message_id, user):
    """Returns a message object from the notification or message table. Or None if the message does not exist.
    Note: A message id may exist but not for the currently logged in user. A user can only see his own messages."""

    message = None
    try:
        message = UserNotification.objects.get(id=message_id, user=user)
    except UserNotification.DoesNotExist:
        message = None

    return message

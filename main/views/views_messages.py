from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from main.forms.forms_user import UserMessageOptionsForm, WriteMessageForm
from main.tables.tables import UserMessageTable
from main.models import User, UserMessage, UserNotification


@login_required
def messages_view(request):
    """Shows the user message inbox and a form to set the message notification policy. In the model there are two
    kinds of messages: the Notifications (result of a subscribed object changing) and the Messages (messages from
    other users or the system). This view shows a table with those combined."""
    user_message_data = list()
    user_messages = UserMessage.objects.filter(receiving_user=request.user).order_by('-sending_time')
    user_notifications = UserNotification.objects.filter(user=request.user).order_by('-sending_time')

    for msg in user_messages:
        user_message_data.append({'message_type': 'message',
                                  'pk': msg.id,
                                  'viewing_state': msg.viewing_state,
                                  'sending_user': msg.sending_user,
                                  'subject': msg.subject,
                                  'sending_time': msg.sending_time})
    for notif in user_notifications:
        user_message_data.append({'message_type': 'notification',
                                  'pk': notif.id,
                                  'viewing_state': notif.viewing_state,
                                  'sending_user': 'Transcriptiones',
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
def message_user_view(request, username, subject='', message=''):
    """Allows a user to send a message to another user."""

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
def messages_mark_unread_view(request, message_type, message_id):
    message = get_message(message_type, message_id, request.user)
    if message is None:
        messages.error(request, _('This message does not exist or does not belong to you.'))
        return HttpResponseRedirect(reverse('main:messages'))

    message.viewing_state = 0
    message.save()
    return HttpResponseRedirect(reverse('main:messages'))


@login_required
def messages_reply_view(request, message_id):
    message = get_message('message', message_id, request.user)
    if message is None:
        messages.error(request, _('This message does not exist or does not belong to you.'))
        return redirect('main:messages')

    reply_message = f"\n\n\nOn {message.sending_time}, {message.sending_user.username} wrote:\n"
    message_lines = message.message.split("\n")
    for line in message_lines:
        reply_message += ">> " + line + "\n"

    return message_user_view(request, message.sending_user.username, subject='Re: ' + message.subject,
                             message=reply_message)


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
    the_messages = UserMessage.objects.filter(receiving_user=request.user)
    for a_message in the_messages:
        a_message.delete()

    the_notifications = UserNotification.objects.filter(user=request.user)
    for a_notification in the_notifications:
        a_notification.delete()

    messages.success(request, _('All messages have been deleted.'))
    return redirect('main:messages')


def get_message(message_type, message_id, user):
    """Returns a message object from the notification or message table. Or None if the message does not exist.
    Note: A message id may exist but not for the currently logged in user. A user can only see his own messages."""

    message = None
    if message_type == 'message':
        try:
            message = UserMessage.objects.get(id=message_id, receiving_user=user)
        except UserMessage.DoesNotExist:
            message = None
    if message_type == 'notification':
        try:
            message = UserNotification.objects.get(id=message_id, user=user)
        except UserMessage.DoesNotExist:
            message = None

    return message

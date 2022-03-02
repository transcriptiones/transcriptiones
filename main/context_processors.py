import datetime

from django.urls import reverse

from main.models import UserMessage, UserNotification, ContactMessage


def user_notifications(request):
    """Returns unread notifications of a user. Notifications in this context mean all messages a user can get. They
    can be notifications on changes of a subscribed object or system/user messages. This request only returns the last
    three unread notifications and the number of total unread messages."""

    if request.user.is_authenticated:
        new_messages = UserMessage.objects.filter(receiving_user=request.user, viewing_state=0).order_by('-sending_time')[:3]
        new_user_notifications = UserNotification.objects.filter(user=request.user, viewing_state=0).order_by('-sending_time')[:3]
        new_notifications = list()
        for msg in new_messages:
            new_notifications.append({'url': reverse('main:messages_read', args=['message', msg.id]),
                                      'sender': msg.sending_user.username,
                                      'user_color': msg.sending_user.get_user_color(),
                                      'subject': msg.subject,
                                      'sending_time': msg.sending_time})
        for msg in new_user_notifications:
            new_notifications.append({'url': reverse('main:messages_read', args=['notification', msg.id]),
                                      'sender': 'Transcriptiones',
                                      'user_color': '#CCCCCC',
                                      'subject': msg.subject,
                                      'sending_time': msg.sending_time})
        new_notifications = sorted(new_notifications, key=lambda d: d['sending_time'], reverse=True)
        new_notifications = new_notifications[:3]

        cnt = ContactMessage.objects.filter(state=0).count()
        # print(cnt, request.user.is_superuser)
        total_new_notifications = new_messages.count() + new_user_notifications.count()

        if request.user.is_superuser and cnt > 0:
            new_notifications.append({'url': reverse('main:admin_inbox'),
                                      'sender': "ADMIN",
                                      'user_color': '#CCCCCC',
                                      'subject': "Unanswered Contact Messages",
                                      'sending_time': datetime.datetime.now()})
            total_new_notifications += 1

    else:
        new_notifications = []
        total_new_notifications = 0

    # print(new_notifications)
    return {'cp_user_notifications': new_notifications,
            'cp_total_new_notifications': total_new_notifications}

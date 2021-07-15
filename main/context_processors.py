from django.conf import settings  # import the settings file

from main.models import UserMessage, UserNotification


def user_notifications(request):
    if request.user.is_authenticated:
        new_messages = UserMessage.objects.filter(receiving_user=request.user, viewing_state=0).count()
        new_notifications = UserNotification.objects.filter(user=request.user, viewing_state=0).count()
    else:
        new_messages = 0
        new_notifications = 0

    return {'user_messages': new_messages,
            'user_subscriptions': new_notifications}

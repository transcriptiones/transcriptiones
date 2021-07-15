from django.conf import settings  # import the settings file

from main.models import UserMessage


def user_notifications(request):
    if request.user.is_authenticated:
        new_messages = UserMessage.objects.filter(receiving_user=request.user, viewing_state=0, message_type=0).count()
        new_notifications = UserMessage.objects.filter(receiving_user=request.user, viewing_state=0, message_type=1).count()
    else:
        new_messages = 0

    return {'user_messages': new_messages,
            'user_subscriptions': new_notifications}

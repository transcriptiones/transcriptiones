import time

from django.db.models import Q

from main.models import ContactMessage, User


def send_daily_notification_email():
    users_to_notify = User.objects.filter(Q(notification_policy=User.NotificationPolicy.DAILY) |
                                          Q(message_notification_policy=User.MessageNotificationPolicy.DAILY))

    # Process all users who get daily mails (either for messages or notifications)
    for usr in users_to_notify:
        # If this user wants daily Notifications of Notifications
        if usr.notification_policy == User.NotificationPolicy.DAILY:
            unread_notifications = usr.usernotification_set.filter(viewing_state=0)
        # If this user wants daily Notifications of Notifications
        if usr.message_notification_policy == User.MessageNotificationPolicy.DAILY:
            unread_messages = usr.usermessage_set.filter(viewing_state=0)



def send_weekly_notification_email():
    # print("Executing a cron job...")
    time.sleep(10)
    # print("Done!")

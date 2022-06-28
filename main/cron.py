import datetime
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from main.mail_utils import send_daily_notification_mail, send_weekly_notification_mail
from main.models import User, Document, UserSubscription, RefNumber, Institution


def send_administration_email():
    print("Admin-Email not yet implemented")


def send_daily_notification_email():
    datetime_a_day_ago = timezone.now() - datetime.timedelta(hours=24)
    users_to_notify = User.objects.filter(notification_policy=User.NotificationPolicy.DAILY)

    notification_list = get_notification_list_since(users_to_notify, datetime_a_day_ago)
    for notification in notification_list:
        send_daily_notification_mail(notification["user"], notification["text"])


def send_weekly_notification_email(user=None):
    print("send weekly")
    """For each user with a weekly notification policy, all changes in all subscriptions are counted and parsed into
     HTML and sent as an e-mail."""
    datetime_a_week_ago = timezone.now() - datetime.timedelta(days=7)
    users_to_notify = User.objects.filter(notification_policy=User.NotificationPolicy.WEEKLY)
    if user is not None:
        print(f"ONLY SENDING TEST TO USER {user.username}")
        users_to_notify = [user, ]

    notification_list = get_notification_list_since(users_to_notify, datetime_a_week_ago)
    for notification in notification_list:
        send_weekly_notification_mail(notification["user"], notification["text"])


def get_notification_list_since(users_to_notify, past_datetime):
    user_email_texts = list()
    for usr in users_to_notify:
        # Get all the subscriptions from user
        user_subscriptions = UserSubscription.objects.filter(user=usr).order_by('subscription_type')

        total_documents_changed = 0
        notification_messages = list()
        for notification in user_subscriptions:
            notification_message = ""
            # Document-subscription: check for changes in this document
            if notification.subscription_type == UserSubscription.SubscriptionType.DOCUMENT:
                try:
                    doc_in_subscription = Document.all_objects.get(id=notification.object_id)
                    changes = Document.all_objects.filter(document_id=doc_in_subscription.document_id,
                                                          document_utc_add__gt=past_datetime)
                    notification_message = _(f"There were {changes.count()} changes in your document subscription "
                                             f"<strong>{doc_in_subscription.title_name}</strong>.")
                    if changes.count() > 0:
                        notification_message += _(f"The last commit message is: <i>{changes.last().commit_message}</i>")
                        total_documents_changed += 1
                except Document.DoesNotExist:
                    notification_message = _("There is a problem with your subscription.")

            # Ref-number-subscription: check for changes in this reference number
            elif notification.subscription_type == UserSubscription.SubscriptionType.REF_NUMBER:
                try:
                    ref_in_subscription = RefNumber.objects.get(id=notification.object_id)
                    changes = Document.objects.filter(parent_ref_number=ref_in_subscription,
                                                      document_utc_add__gt=past_datetime)
                    notification_message = _(f"{changes.count()} documents changed in your reference number "
                                             f"subscription. <strong>{ref_in_subscription.ref_number_title}</strong>.")
                    total_documents_changed += changes.count()
                except RefNumber.DoesNotExist:
                    notification_message = _("There is a problem with your subscription.")

            # User subscription: check for changes made by this user
            elif notification.subscription_type == UserSubscription.SubscriptionType.USER:
                try:
                    user_in_subscription = User.objects.get(id=notification.object_id)
                    changes = Document.all_objects.filter(submitted_by=user_in_subscription,
                                                          publish_user=True,
                                                          document_utc_add__gt=past_datetime)
                    unique_changes = Document.objects.filter(submitted_by=user_in_subscription,
                                                             publish_user=True,
                                                             document_utc_add__gt=past_datetime)
                    notification_message = _(f"The user <strong>{user_in_subscription.username}</strong> made "
                                             f"{changes.count()} changes in {unique_changes.count()}. documents.")
                    total_documents_changed += unique_changes.count()
                except User.DoesNotExist:
                    notification_message = _("There is a problem with your subscription.")

            elif notification.subscription_type == UserSubscription.SubscriptionType.INSTITUTION:
                try:
                    institution_in_subscription = Institution.objects.get(id=notification.object_id)
                    changes = Document.objects.filter(
                        parent_ref_number__holding_institution=institution_in_subscription,
                        document_utc_add__gt=past_datetime)
                    notification_message = _(f"{changes.count()} documents changed in your institution "
                                             f"subscription. <strong>{institution_in_subscription.institution_name}</strong>.")
                    total_documents_changed += changes.count()
                except Institution.DoesNotExist:
                    notification_message = _("There is a problem with your subscription.")

            notification_messages.append(notification_message)

        changelist = _(
            f"There are a total of <strong>{total_documents_changed}</strong> changes in your subscriptions:")
        changelist += "<ul>\n"
        for n in notification_messages:
            changelist += f"  <li>{n}</li>\n"
        changelist += "</ul>"

        if total_documents_changed > 0:
            user_email_texts.append({"user": usr,
                                     "text": changelist})

    return user_email_texts

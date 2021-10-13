from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from main.tokens import account_activation_token
from main.models import ContactMessage
from transcriptiones.settings import NO_REPLY_EMAIL


def send_contact_message_copy(msg: ContactMessage):
    """Send a contact message copy to the email address sending it."""
    subject = _("Thank you for contacting us")
    plain_message = _("We received the following message from you. "
                      "We will contact you as soon as possible. "
                      "Please do not reply to this e-mail address.\n\nYour Message:\n"
                      f"Subject: {msg.subject}\n"
                      f"Message: {msg.message}")
    html_message = ''
    send_transcriptiones_mail(subject, plain_message, html_message, NO_REPLY_EMAIL, msg.reply_email)


def send_daily_notification_mail(user):
    """Sends a mail with the daily notifications of a user."""
    subject = _('Transcriptiones: Daily digest of your notifications')
    plain_message = _('')
    html_message = ''
    send_transcriptiones_mail(subject, plain_message, html_message, NO_REPLY_EMAIL, user.email)


def send_instant_notification_mail(user, subject):
    """Sends a notification email."""
    plain_message = _('')
    html_message = ''
    send_transcriptiones_mail(subject, plain_message, html_message, NO_REPLY_EMAIL, user.email)


def send_username_request_mail(user):
    """A user might forget his username. He can retrieve it by email by entering his email address."""

    subject = _('Transcriptiones: Your User Name')
    plain_message = _(f'Your Username is: {user.username}')
    html_message = ''
    send_transcriptiones_mail(subject, plain_message, html_message, NO_REPLY_EMAIL, user.email)


def send_registration_confirmation_mail(user, current_site):
    """After a user registers, he gets an account activation email."""

    subject = _('Transcriptiones: Please activate your account')
    html_message = render_to_string('main/users/email_templates/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    plain_message = ''
    send_transcriptiones_mail(subject, plain_message, html_message, NO_REPLY_EMAIL, user.email)


def send_transcriptiones_mail(subject, plain_message, html_message, from_email, to_email):
    """Sends an Email to a single recipient in a plain text and html version."""
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)


def get_document_subscription_message(user, document):
    text = f'Hi {user.username}\n\n' \
           f'The document {document.title_name} has changed.\n\n' \
           f'View the the document: <a href="{document.get_absolute_url()}">here</a>\n' \
           f'Manage your subscriptions: <a href="{reverse("main:subscriptions")}">here</a>\n\n' \
           f'Best regards from the Transcriptiones Team'
    return text


def get_reference_subscription_message(user, ref_number):
    text = f'Hi {user.username}\n\n' \
           f'Documents with the reference number {ref_number.ref_number_name} have changed.\n\n' \
           f'View the the reference number: <a href="{ref_number.get_absolute_url()}">here</a>\n' \
           f'Manage your subscriptions: <a href="{reverse("main:subscriptions")}">here</a>\n\n' \
           f'Best regards from the Transcriptiones Team'
    return text


def get_user_subscription_message(subscribing_user, user):
    text = f'Hi {subscribing_user.username}\n\n' \
           f'The user {user.username} has changed data.\n\n' \
           f'View the the users activity: <a href="{reverse("main:")}">here</a>\n' \
           f'Manage your subscriptions: <a href="{reverse("main:subscriptions")}">here</a>\n\n' \
           f'Best regards from the Transcriptiones Team'
    return text

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _

from main.tokens import account_activation_token
from transcriptiones.settings import NO_REPLY_EMAIL


def send_username_request_mail(user):
    subject = _('Transcriptiones: Your User Name')
    message = _(f'Your Username is: {user.username}')
    send_transcriptiones_mail(subject, message, NO_REPLY_EMAIL, user.email)


def send_registration_confirmation_mail(user, current_site):
    subject = _('Transcriptiones: Please activate your account')
    message = render_to_string('main/users/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    send_transcriptiones_mail(subject, message, NO_REPLY_EMAIL, user.email)


def send_transcriptiones_mail(subject, message, from_email, to_email):
    print("SENDING MAIL. TO:", to_email, ", SUBJECT:", subject)
    send_mail(subject, message, from_email, [to_email])


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

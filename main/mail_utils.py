import os
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from main.tokens import account_activation_token
from main.models import ContactMessage
from transcriptiones import settings
from transcriptiones.settings import NO_REPLY_EMAIL


def get_base_render_object(title):
    return {
        'mail_logo_url': 'http://transcriptiones.ch',
        'mail_greetings': _('Best regards') + "<br/>" + _('Your transcriptiones team'),
        'mail_disclaimer': _('This email was sent to you by transcriptiones.ch.') + "<br/>" +
                           _('You received this email because you registered an account on our web site. '
                             'We respect and protect your privacy.') +
                           "<br/>" +
                           _('If you don\'t want to receive our emails, please visit transcriptiones.ch '
                             'and update your settings.'),
        'mail_title': title,
        'mail_paragraphs': []
    }


def send_contact_message_copy(msg: ContactMessage):
    """Send a contact message copy to the email address sending it."""
    subject = _("Thank you for contacting us")
    plain_message = _("We received the following message from you. "
                      "We will contact you as soon as possible. "
                      "Please do not reply to this e-mail.\n\nYour Message:\n"
                      f"Subject: {msg.subject}\n"
                      f"Message: {msg.message}")

    render_object = get_base_render_object(subject)
    render_object["mail_paragraphs"].append(_("We received the following message from you. "
                                              "We will contact you as soon as possible. "
                                              "Please do not reply to this e-mail."))
    render_object["mail_paragraphs"].append('<br/>' + _('Your Message:')+'<br/>' +
                                            f"<b>{msg.subject}</b>\n" + msg.message)
    html_message = render_to_string('main/users/email_templates/base_mail.html', render_object)
    send_transcriptiones_mail(subject, plain_message, html_message, NO_REPLY_EMAIL, msg.reply_email)


def send_batch_upload_request_mail(email_address):
    """Send a confirmation message to someone asking for a batch upload."""
    subject = _('Batch upload request received')
    plain_message = _('Thank you! We received your request for an assisted batch upload and will contact you shortly.')
    render_object = get_base_render_object(_('Thank you for your request'))
    render_object["mail_paragraphs"].append(plain_message)
    html_message = render_to_string('main/users/email_templates/base_mail.html', render_object)
    send_transcriptiones_mail(subject, plain_message, html_message, NO_REPLY_EMAIL, email_address)


def send_daily_notification_mail(user):
    """Sends a mail with the daily notifications of a user."""
    subject = _('Daily digest of your notifications')
    plain_message = _('These are your unread notifications:')   # TODO print notifications
    render_object = get_base_render_object(_('Today\'s changes'))
    render_object["mail_paragraphs"].append(plain_message)
    html_message = render_to_string('main/users/email_templates/base_mail.html', render_object)
    send_transcriptiones_mail(subject, plain_message, html_message, NO_REPLY_EMAIL, user.email)


def send_weekly_notification_mail(user):
    """Sends a mail with the daily notifications of a user."""
    subject = _('Weekly digest of your notifications')
    plain_message = _('These are your unread notifications:')   # TODO print notifications
    render_object = get_base_render_object(_('This week\'s changes'))
    render_object["mail_paragraphs"].append(plain_message)
    html_message = render_to_string('main/users/email_templates/base_mail.html', render_object)
    send_transcriptiones_mail(subject, plain_message, html_message, NO_REPLY_EMAIL, user.email)


def send_instant_notification_mail(user, notification):
    """Sends a notification email."""
    subject = _('A Message from transcriptiones.ch')
    plain_message = _('You received a message:')                # TODO print message
    render_object = get_base_render_object(_('You received a message'))
    render_object["mail_paragraphs"].append(plain_message)
    html_message = render_to_string('main/users/email_templates/base_mail.html', render_object)
    send_transcriptiones_mail(subject, plain_message, html_message, NO_REPLY_EMAIL, user.email)


def send_username_request_mail(to_address):
    """A user might forget his username. He can retrieve it by email by entering his email address."""
    # TODO retrieve username
    subject = _('Transcriptiones: Your User Name')
    plain_message = _(f'Your Username is: ???')
    render_object = get_base_render_object(_('Your username'))
    render_object["mail_paragraphs"].append(plain_message)
    html_message = render_to_string('main/users/email_templates/base_mail.html', render_object)
    send_transcriptiones_mail(subject, plain_message, html_message, NO_REPLY_EMAIL, to_address)


def send_password_reset_mail(user):
    subject = _('Transcriptiones: Password Reset')
    plain_message = _(f'Your Username is: {user.username}. Goto LINK to reset your password.')
    render_object = get_base_render_object(_('Password reset'))
    render_object["mail_paragraphs"].append(plain_message)
    html_message = render_to_string('main/users/email_templates/base_mail.html', render_object)
    send_transcriptiones_mail(subject, plain_message, html_message, NO_REPLY_EMAIL, user.email)


def send_registration_confirmation_mail(user):
    """After a user registers, he gets an account activation email."""

    subject = _('Transcriptiones: Activate your account')
    plain_message = _('Dummy content')      # TODO

    render_object = get_base_render_object(_('Activate your account'))
    render_object["mail_paragraphs"].append(plain_message)
    render_object["user"] = user
    render_object["domain"] = 'transcriptiones.ch'
    render_object["uid"] = urlsafe_base64_encode(force_bytes(user.pk))
    render_object["token"] = account_activation_token.make_token(user)

    html_message = render_to_string('main/users/email_templates/account_activation_email.html', render_object)
    send_transcriptiones_mail(subject, plain_message, html_message, NO_REPLY_EMAIL, user.email)


def send_transcriptiones_mail(subject, plain_message, html_message, from_email, to_email):
    """Sends an Email to a single recipient in a plain text and html version."""

    new_message = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=NO_REPLY_EMAIL,
        to=[to_email, ],
        reply_to=[NO_REPLY_EMAIL, ]
    )

    new_message.attach_alternative(html_message, "text/html")
    new_message.content_subtype = 'html'
    new_message.mixed_subtype = 'related'
    img_path = os.path.join(settings.STATIC_ROOT, 'main', 'images', 'logo_blue.png')

    with open(img_path, 'rb') as banner_image:
        banner_image = MIMEImage(banner_image.read())
        banner_image.add_header('Content-ID', '<logo-image.png>')
        new_message.attach(banner_image)

    new_message.send()


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

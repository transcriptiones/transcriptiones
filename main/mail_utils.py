import os
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from main.tokens import account_activation_token
from transcriptiones import settings
from transcriptiones.settings import NO_REPLY_EMAIL
from lxml import html
from lxml.html.clean import clean_html


def get_basest_base_render_object():
    """Returns an object to render a html message. Used for messages sent by the cron job"""
    return {
        'mail_greetings': _('Best regards') + "<br/>" + _('Your transcriptiones team'),
        'mail_disclaimer': _('This email was sent to you by transcriptiones.ch.') + "<br/>" +
                           _('You received this email because you registered an account on our web site. '
                             'We respect and protect your privacy.') +
                           "<br/>" +
                           _('If you don\'t want to receive our emails, please visit transcriptiones.ch '
                             'and update your settings.'),
        'mail_paragraphs': []
    }


def get_base_render_object(request, subject):
    """Returns an object to render a html message. Used for all messages """

    basest_base = get_basest_base_render_object()
    basest_base.update({
        'mail_logo_url': request.get_host(),
        'mail_title': subject,
    })
    return basest_base


def create_message(request, subject, message):
    render_object = get_base_render_object(request, subject)
    render_object["mail_paragraphs"] = [message,]
    html_message = render_to_string('main/users/email_templates/base_mail.html', render_object)
    plain_message = message.replace("<br/>", "\n")
    tree = html.fromstring(plain_message)
    plain_message = clean_html(tree).text_content().strip()
    return plain_message, html_message


def create_message_without_request(subject, message):
    render_object = get_basest_base_render_object()
    render_object.update({
        'subject': subject,
        'mail_logo_url': 'https://transcriptiones.ch'
    })
    render_object["mail_paragraphs"] = [message, ]
    html_message = render_to_string('main/users/email_templates/base_mail.html', render_object)
    plain_message = message.replace("<br/>", "\n")
    tree = html.fromstring(plain_message)
    plain_message = clean_html(tree).text_content().strip()
    return plain_message, html_message


def send_deactivation_mail(request, email_address):
    """Sends a mail after a user has been deactivated"""

    subject = _("Your account has been deactivated")
    plain_message, html_message = create_message(request,
                                                 subject,
                                                 _("Your account has been deactivated. You cannot login anymore."))
    send_transcriptiones_mail(subject, plain_message, html_message, email_address)


def send_newsletter_subscribe_mail(request, email_address):
    """Sends a mail after a person subscribed to transcriptiones """

    subject = _("Thank you for subscribing to our Newsletter")
    plain_message, html_message = create_message(request,
                                                 subject,
                                                 _("Thank you for subscribing to transcriptiones.ch. "
                                                    "We will send you the latest news."))
    send_transcriptiones_mail(subject, plain_message, html_message, email_address)


def send_user_message_mail(request, message):
    """Sends a mail after a person subscribed to transcriptiones
        Takes a UserMessage
     """

    subject = _("You received a message")
    plain_message, html_message = create_message(request,
                                                 subject,
                                                 _(f"You received a message from {message.sending_user.username}."))
    send_transcriptiones_mail(subject, plain_message, html_message, message.receiving_user.email)


def send_contact_message_copy(request, msg):
    """Send a contact message copy to the email address sending it.
        Takes a ContactMessage
    """

    subject = _("Thank you for contacting us")
    plain_message, html_message = create_message(request,
                                                 subject,
                                                 "We received the following message from you. "
                                                 "We will contact you as soon as possible.<br/>"
                                                 "Please do not reply to this email."
                                                 "<br/>Your Message:<br/>"
                                                 f"Subject: <b>{msg.subject}</b><br/>"
                                                 f"Message: {msg.message}")
    send_transcriptiones_mail(subject, plain_message, html_message, msg.reply_email)


def send_contact_message_answer(request, msg):
    """Send a contact message copy anser to the email address sending it.
        Takes a ContactMessage
    """

    subject = msg.answer_subject
    plain_message, html_message = create_message(request,
                                                 subject,
                                                 msg.answer.replace("\n", "<br/>"))
    send_transcriptiones_mail(subject, plain_message, html_message, msg.reply_email)


def send_changed_address_mail(request, user):
    subject = _('transcriptiones: New Email address')
    plain_message, html_message = create_message(request,
                                                 subject,
                                                 _(f"Your New Email address is: {user.email}"))
    send_transcriptiones_mail(subject, plain_message, html_message, user.email)


def send_username_request_mail(request, user):
    """A user might forget his username. He can retrieve it by email by entering his email address.
        Takes a User
    """

    subject = _('transcriptiones: Your User Name')
    plain_message, html_message = create_message(request,
                                                 subject,
                                                 _(f"Your Username is: {user.username}"))
    send_transcriptiones_mail(subject, plain_message, html_message, user.email)


def send_password_reset_mail(request, user):
    """Takes a User"""
    subject = _('transcriptiones: Password Reset')
    url = ''
    plain_message, html_message = create_message(request,
                                                 subject,
                                                 _(f"Your Username is: {user.username}. Go to {url} to reset your password."))
    send_transcriptiones_mail(subject, plain_message, html_message, user.email)


    """# plain_message = _(f'Your Username is: {user.username}. Goto LINK to reset your password.')
    render_object = get_base_render_object(request, _('Password reset'))
    render_object["mail_paragraphs"].append(plain_message)
    html_message = render_to_string('main/users/email_templates/base_mail.html', render_object)
    send_transcriptiones_mail(subject, plain_message, html_message, user.email)"""


def send_registration_confirmation_mail(request, user):
    """After a user registers, he gets an account activation email."""

    subject = _('transcriptiones: Activate your account')
    host = f"{request.scheme}://{request.get_host()}"

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    url = reverse('main:activate', kwargs={'uidb64': uid, 'token': token})
    plain_message = _(f'Hi { user.username }!\n\n'
                      'A warm welcome from the transcriptiones team. '
                      'Please click the following Link or copy it in your browser '
                      'to finalize your registration on transcriptiones.\n\n'
                      f'Activation-Link: {host}{url}')

    render_object = get_base_render_object(request, _('Activate your account'))
    render_object["mail_paragraphs"].append(plain_message)
    render_object["user"] = user
    render_object["domain"] = host
    render_object["uid"] = uid
    render_object["token"] = token

    html_message = render_to_string('main/users/email_templates/account_activation_email.html', render_object)
    send_transcriptiones_mail(subject, plain_message, html_message, user.email)


def send_daily_notification_mail(user, notification_message):
    """Sends a mail with the daily notifications of a user."""
    subject = _('Daily digest of your notifications')
    plain_message, html_message = create_message_without_request(subject, notification_message)
    send_transcriptiones_mail(subject, plain_message, html_message, user.email)


def send_weekly_notification_mail(user, notification_message):
    """Sends a mail with the daily notifications of a user."""
    subject = _('Weekly digest of your notifications')
    plain_message, html_message = create_message_without_request(subject, notification_message)
    send_transcriptiones_mail(subject, plain_message, html_message, user.email)


def send_instant_notification_mail(request, user, notification):
    """Sends a notification email."""
    subject = _('A Message from transcriptiones.ch')
    plain_message = _('You received a message:')                # TODO print message
    render_object = get_base_render_object(request, _('You received a message'))
    render_object["mail_paragraphs"].append(plain_message)
    html_message = render_to_string('main/users/email_templates/base_mail.html', render_object)
    send_transcriptiones_mail(subject, plain_message, html_message, user.email)


def send_transcriptiones_mail(subject, plain_message, html_message, to_email):
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

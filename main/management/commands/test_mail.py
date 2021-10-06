import os

from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from main.mail_utils import send_transcriptiones_mail

from django.core.management.base import BaseCommand, CommandError

from main.models import User
from main.tokens import account_activation_token
from transcriptiones import settings


class Command(BaseCommand):
    help = 'Tests if sending an e-mail works.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('to_address', type=str)

    def handle(self, *args, **options):
        to_address = options['to_address']
        user = User.objects.get(username=options['username'])
        self.stdout.write(self.style.SUCCESS('Testing mail settings.'))
        subject = 'Transcriptiones: Please activate your account'
        html_message = render_to_string('main/users/email_templates/account_activation_email.html', {
            'user': user,
            'domain': 'transcriptiones.ch',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        plain_message = ''
        send_transcriptiones_mail(subject, 'plain message', html_message, settings.NO_REPLY_EMAIL, to_address)
        self.stdout.write(self.style.SUCCESS('Tried to send mail.'))

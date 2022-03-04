import main.mail_utils as mail_utils
from django.core.management.base import BaseCommand
from main.models import User, ContactMessage

# TODO rewrite mail test

class Command(BaseCommand):
    help = 'Tests if sending an e-mail works.'

    def add_arguments(self, parser):
        parser.add_argument('which_test', type=str)
        parser.add_argument('username', type=str)
        parser.add_argument('to_address', type=str)


    def handle(self, *args, **options):
        my_options = ['all', 'contact', 'daily', 'weekly', 'instant', 'pw_reset', 'register', 'batch', 'username']
        if options['which_test'] not in my_options:
            self.stdout.write(self.style.ERROR(f'"which_test" must be one of "{", ".join(my_options)}"'))

        to_address = options['to_address']
        user = User.objects.get(username=options['username'])

        if options['which_test'] == "contact" or options['which_test'] == "all":
            msg = ContactMessage()
            msg.subject = 'Your Contact Subject line'
            msg.message = 'Your Contact message'
            msg.reply_email = options['to_address']
            mail_utils.send_contact_message_copy(msg)
            self.stdout.write(self.style.SUCCESS('Sent contact mail.'))

        if options['which_test'] == "daily" or options['which_test'] == "all":
            mail_utils.send_daily_notification_mail(user)
            self.stdout.write(self.style.SUCCESS('Sent daily mail.'))

        if options['which_test'] == "weekly" or options['which_test'] == "all":
            mail_utils.send_weekly_notification_mail(user)
            self.stdout.write(self.style.SUCCESS('Sent weekly mail.'))

        if options['which_test'] == "instant" or options['which_test'] == "all":
            mail_utils.send_instant_notification_mail(user, 'Something has changed')
            self.stdout.write(self.style.SUCCESS('Sent instant mail.'))

        if options['which_test'] == "pw_reset" or options['which_test'] == "all":
            mail_utils.send_password_reset_mail(user)
            self.stdout.write(self.style.SUCCESS('Sent pasword reset mail.'))

        if options['which_test'] == "register" or options['which_test'] == "all":
            mail_utils.send_registration_confirmation_mail(user, "http://domain.of.installati.on/")
            self.stdout.write(self.style.SUCCESS('Sent registration confirmation mail.'))

        if options['which_test'] == "batch" or options['which_test'] == "all":
            mail_utils.send_batch_upload_request_mail(options['to_address'])
            self.stdout.write(self.style.SUCCESS('Sent batch mail.'))

        if options['which_test'] == "username" or options['which_test'] == "all":
            mail_utils.send_username_request_mail(user)
            self.stdout.write(self.style.SUCCESS('Sent batch mail.'))

        self.stdout.write('Test finished.')

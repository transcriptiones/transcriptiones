from django.core.management.base import BaseCommand

from main.cron import send_weekly_notification_email
from main.models import User


class Command(BaseCommand):
    help = 'Tests if sending an email works.'

    def add_arguments(self, parser):
        parser.add_argument('which_test', type=str)
        parser.add_argument('which_user', type=str)

    def handle(self, *args, **options):
        self.stdout.write('Starting cron test.')

        my_options = ['daily', 'weekly']
        if options['which_test'] not in my_options:
            self.stdout.write(self.style.ERROR(f'"which_test" must be one of "{", ".join(my_options)}"'))

        try:
            user = User.objects.get(username=options['which_user'])
        except User.DoesNotExist:
            self.stdout.write('User not found... aborting.')
            return

        if options['which_test'] == my_options[1]:
            self.stdout.write('Test weekly.')
            send_weekly_notification_email(user=user)

        self.stdout.write('Test finished.')

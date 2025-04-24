from django.core.management.base import BaseCommand
from main.cleanup import cleanup_all

class Command(BaseCommand):
    help = 'Cleans up the database manually.'

    def add_arguments(self, parser):
        parser.add_argument('hours', type=int, default=48)
        parser.add_argument('dry run', type=bool, default=True)

    def handle(self, *args, **options):
        cleanup_all(hours=options['hours'], dry_run=options['dry run'])

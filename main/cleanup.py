import datetime

from django.db.models import Count
from django.utils import timezone
from main.models import User, Author, RefNumber, Institution


def cleanup_users(hours = 48):
    users = User.objects.annotate(d_count=Count('contributions')).filter(email_confirmed=False,
                                                                         is_active=False,
                                                                         date_joined__lte=timezone.now() - datetime.timedelta(hours=hours),
                                                                         d_count=0)

    for user in users:
        user.delete()


def cleanup_inst(hours=48):
    insts = Institution.objects.annotate(ref_count=Count('refnumber')).filter(ref_count=0,
                                                                                  institution_utc_add__lte=timezone.now() - datetime.timedelta(hours=hours))
    for inst in insts:
        inst.delete()


def cleanup_ref(hours=48):
    refs = RefNumber.objects.annotate(doc_count=Count('document')).filter(doc_count=0,
                                                                            ref_number_utc_add__lte=timezone.now() - datetime.timedelta(hours=hours))
    for ref in refs:
        ref.delete()

def cleanup_author(hours=48):
    authors = Author.objects.annotate(doc_count=Count('document')).filter(doc_count=0,
                                                                               author_utc_add__lte=timezone.now() - datetime.timedelta(hours=hours))
    for author in authors:
        author.delete()

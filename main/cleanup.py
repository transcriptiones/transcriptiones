import datetime

from django.db.models import Count
from django.utils import timezone
from main.models import User, Author, RefNumber, Institution


def cleanup_all(hours=48, dry_run=True):
    cleanup_users(hours, dry_run)
    cleanup_inst(hours, dry_run)
    cleanup_ref(hours, dry_run)
    cleanup_author(hours, dry_run)


def cleanup_users(hours=48, dry_run=True):
    users = User.objects.annotate(d_count=Count('contributions')).filter(email_confirmed=False,
                                                                         is_active=False,
                                                                         date_joined__lte=timezone.now() - datetime.timedelta(hours=hours),
                                                                         d_count=0)

    if dry_run:
        with open("users_to_delete.txt", "w", encoding='utf-8') as f:
            for user in users:
                f.write(f"{user.username}\n")
        return

    for user in users:
        user.delete()


def cleanup_inst(hours=48, dry_run=True):
    insts = Institution.objects.annotate(ref_count=Count('refnumber')).filter(ref_count=0,
                                                                              institution_utc_add__lte=timezone.now() - datetime.timedelta(hours=hours),
                                                                              ref_url_required=False)

    if dry_run:
        with open("insts_to_delete.txt", "w", encoding='utf-8') as f:
            for inst in insts:
                f.write(f"{inst.institution_name}\n")
        return

    for inst in insts:
        inst.delete()


def cleanup_ref(hours=48, dry_run=True):
    refs = RefNumber.objects.annotate(doc_count=Count('document')).filter(doc_count=0,
                                                                          ref_number_utc_add__lte=timezone.now() - datetime.timedelta(hours=hours))

    if dry_run:
        with open("refs_to_delete.txt", "w", encoding='utf-8') as f:
            for ref in refs:
                f.write(f"{ref.ref_number_name}\n")
        return

    for ref in refs:
        ref.delete()

def cleanup_author(hours=48, dry_run=True):
    authors = Author.objects.annotate(doc_count=Count('document')).filter(doc_count=0,
                                                                          author_utc_add__lte=timezone.now() - datetime.timedelta(hours=hours))

    if dry_run:
        with open("authors_to_delete.txt", "w", encoding='utf-8') as f:
            for author in authors:
                f.write(f"{author.author_name}\n")
        return
    for author in authors:
        author.delete()

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from django.core import serializers
from django_tables2 import RequestConfig

from main import models
import zipfile
import os

from main.filters import UserFilter
from main.models import ContactMessage, User
from main.tables.tables import ContactMessageTable, UserTable


def get_user_or_none(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(_('User does not exist'))
        user = None
    return user


@user_passes_test(lambda u: u.is_superuser)
def activate_user(request, user_id):
    user = get_user_or_none(user_id)
    if user is not None:
        user.is_active = True
        user.save()
        messages.success(request, _('User activated'))
    return redirect('main:admin_users')


@user_passes_test(lambda u: u.is_superuser)
def deactivate_user(request, user_id):
    # TODO send email
    user = get_user_or_none(user_id)
    if user is not None:
        user.is_active = False
        user.save()
        messages.success(request, _('User deactivated'))
    return redirect('main:admin_users')


@user_passes_test(lambda u: u.is_superuser)
def set_user_staff(request, user_id):
    user = get_user_or_none(user_id)
    if user is not None:
        user.is_staff = True
        user.is_superuser = False
        user.save()
        messages.success(request, _('User set to staff'))
    return redirect('main:admin_users')


@user_passes_test(lambda u: u.is_superuser)
def set_user_admin(request, user_id):
    user = get_user_or_none(user_id)
    if user is not None:
        user.is_staff = True
        user.is_superuser = True
        user.save()
        messages.success(request, _('User set to user'))
    return redirect('main:admin_users')


@user_passes_test(lambda u: u.is_superuser)
def set_user_user(request, user_id):
    user = get_user_or_none(user_id)
    if user is not None:
        user.is_staff = False
        user.is_superuser = False
        user.save()
        messages.success(request, _('User set to admin'))
    return redirect('main:admin_users')


@user_passes_test(lambda u: u.is_superuser)
def admin_view(request):
    """Shows a static page with options of an admin user."""
    return render(request, 'main/admin/admin.html')


@user_passes_test(lambda u: u.is_superuser)
def admin_inbox_view(request):
    table = ContactMessageTable(data=ContactMessage.objects.filter(state=0))
    return render(request, 'main/admin/contact_messages.html', {'table': table})


@user_passes_test(lambda u: u.is_superuser)
def admin_users_view(request):
    u_filter = UserFilter(request.GET, queryset=User.objects.all())
    table = UserTable(data=u_filter.qs, current_user=request.user)
    RequestConfig(request).configure(table)

    return render(request, 'main/admin/admin_users.html', {'table': table, 'filter': u_filter})


@user_passes_test(lambda u: u.is_superuser)
def admin_expert_view(request):
    return render(request, 'main/admin/admin_expert.html')


@user_passes_test(lambda u: u.is_superuser)
def admin_statistics_view(request):

    return render(request, 'main/admin/statistics.html')


@user_passes_test(lambda u: u.is_superuser)
def admin_merge_docs_view(request):
    return render(request, 'main/admin/merge_docs.html')


@user_passes_test(lambda u: u.is_superuser)
def admin_export_json_view(request):
    file_name = "transcriptiones.zip"
    zip_file = zipfile.ZipFile(file_name, mode="w", compression=zipfile.ZIP_DEFLATED)

    data_source_type = serializers.serialize("json", models.SourceType.objects.all())
    zip_file.writestr("SourceType.json", data_source_type)

    data_author = serializers.serialize("json", models.Author.objects.all())
    zip_file.writestr("Author.json", data_author)

    data_documents = serializers.serialize("json", models.Document.objects.all())
    zip_file.writestr("Document.json", data_documents)

    data_institutions = serializers.serialize("json", models.Institution.objects.all())
    zip_file.writestr("Institution.json", data_institutions)

    data_ref_numbers = serializers.serialize("json", models.RefNumber.objects.all())
    zip_file.writestr("RefNumber.json", data_ref_numbers)

    zip_file.close()

    response = HttpResponse(open(file_name, 'rb'), content_type="application/zip")
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    os.remove(file_name)
    return response



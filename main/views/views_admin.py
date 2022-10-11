import os
import zipfile
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from django.core import serializers
from django_tables2 import RequestConfig
from main.mail_utils import send_contact_message_answer
from main.filters import UserFilter
from main.forms.forms_admin import ContactMessageReplyForm, SendNewsletterForm
from main.models import ContactMessage, User, RefNumber, Author, SourceType, Document, Institution
from main.tables.tables import ContactMessageTable, UserTable


def get_user_or_none(request, user_id):
    """Returns user object or None if the user is not found.
    Adds an alert message if user not found."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, _('User does not exist'))
        user = None
    return user


@user_passes_test(lambda u: u.is_superuser)
def activate_user(request, user_id):
    """Activate a deactivated user. Admin rights needed"""
    user = get_user_or_none(request, user_id)
    if user is not None:
        user.is_active = True
        user.save()
        messages.success(request, _('User activated'))
    return redirect('main:admin_users')


@user_passes_test(lambda u: u.is_superuser)
def deactivate_user(request, user_id):
    # TODO send email
    user = get_user_or_none(request, user_id)
    if user is not None:
        user.is_active = False
        user.save()
        messages.success(request, _('User deactivated'))
    return redirect('main:admin_users')


@user_passes_test(lambda u: u.is_superuser)
def set_user_staff(request, user_id):
    user = get_user_or_none(request, user_id)
    if user is not None:
        user.is_staff = True
        user.is_superuser = False
        user.save()
        messages.success(request, _('User set to staff'))
    return redirect('main:admin_users')


@user_passes_test(lambda u: u.is_superuser)
def set_user_admin(request, user_id):
    user = get_user_or_none(request, user_id)
    if user is not None:
        user.is_staff = True
        user.is_superuser = True
        user.save()
        messages.success(request, _('User set to user'))
    return redirect('main:admin_users')


@user_passes_test(lambda u: u.is_superuser)
def set_user_user(request, user_id):
    user = get_user_or_none(request, user_id)
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
    if request.method == 'GET':
        show = request.GET.get('show')
        if show == 'all':
            table = ContactMessageTable(data=ContactMessage.objects.all().order_by('-sending_time'))
        elif show == 'unanswered':
            table = ContactMessageTable(data=ContactMessage.objects.exclude(state=2).exclude(state=3).order_by('-sending_time'))
        else:
            table = ContactMessageTable(data=ContactMessage.objects.exclude(state=2).order_by('-sending_time'))
        return render(request, 'main/admin/contact_messages.html', {'table': table})

    if request.method == 'POST':
        pks = request.POST.getlist('select')
        action = request.POST.get('action_options')
        selected_messages = ContactMessage.objects.filter(pk__in=pks)
        if action == 'mark_read':
            for message in selected_messages:
                message.state = 1
                message.save()
            messages.success(request, format_lazy(_('{num_changed} contact messages marked as read'), num_changed=str(len(selected_messages))))
        elif action == 'mark_unread':
            for message in selected_messages:
                message.state = 0
                message.save()
            messages.success(request, format_lazy(_('{num_changed} contact messages marked as unread'), num_changed=str(len(selected_messages))))
        elif action == 'mark_spam':
            for message in selected_messages:
                message.state = 2
                message.save()
            messages.success(request, format_lazy(_('{num_changed} contact messages marked as spam'), num_changed=str(len(selected_messages))))
        elif action == 'mark_answered':
            for message in selected_messages:
                message.state = 3
                message.save()
            messages.success(request, format_lazy(_('{num_changed} contact messages marked as answered'), num_changed=str(len(selected_messages))))
        elif action == 'delete':
            for message in selected_messages:
                message.delete()
            messages.success(request, format_lazy(_('{num_changed} contact messages deleted'), num_changed=str(len(selected_messages))))
        return redirect('main:admin_inbox')


@user_passes_test(lambda u: u.is_superuser)
def admin_inbox_message_view(request, msg_id):
    message = get_object_or_404(ContactMessage, id=msg_id)
    message.save()
    return render(request, 'main/admin/contact_message.html', {'message': message})


@user_passes_test(lambda u: u.is_superuser)
def admin_inbox_message_delete(request, msg_id):
    message = get_object_or_404(ContactMessage, id=msg_id)
    messages.success(request, _('Contact message deleted'))
    message.delete()
    return redirect('main:admin_inbox')


@user_passes_test(lambda u: u.is_superuser)
def admin_inbox_message_answer(request, msg_id):
    message = get_object_or_404(ContactMessage, id=msg_id)
    answer_string = f'Hello {message.reply_email}\n\nThank you for contacting Trancriptiones.\n\n[ENTER MSG]\n\nYour message:\n'
    for part in message.message.split("\n"):
        answer_string += ">> " + part + "\n"

    form = ContactMessageReplyForm({'subject': f'Re: {message.subject}',
                                    'answer': answer_string})

    if request.method == "POST":
        if 'cancel' in request.POST.keys():
            return redirect('main:admin_inbox_message', msg_id=msg_id)

        form = ContactMessageReplyForm(request.POST)

        if form.is_valid():
            if 'submit' in request.POST.keys():
                message.answer_subject = form.cleaned_data['subject']
                message.answer = form.cleaned_data['answer']
                message.state = 3
                message.save()
                send_contact_message_answer(request, message)
                messages.success(request, "The contact message has been answered")
                return redirect('main:admin_inbox_message', msg_id=msg_id)

    return render(request, 'main/admin/contact_message_answer.html', {'message': message, 'form': form})


@user_passes_test(lambda u: u.is_superuser)
def admin_inbox_message_mark_answered(request, msg_id):
    message = get_object_or_404(ContactMessage, id=msg_id)
    messages.success(request, _('Contact message marked as answered'))
    message.state = 3
    message.save()
    return redirect('main:admin_inbox')


@user_passes_test(lambda u: u.is_superuser)
def admin_inbox_message_mark_spam(request, msg_id):
    message = get_object_or_404(ContactMessage, id=msg_id)
    messages.success(request, _('Contact message marked as spam'))
    message.state = 2
    message.save()
    return redirect('main:admin_inbox')

@user_passes_test(lambda u: u.is_superuser)
def admin_inbox_message_mark_read(request, msg_id):
    message = get_object_or_404(ContactMessage, id=msg_id)
    messages.success(request, _('Contact message marked as read'))
    message.state = 1
    message.save()
    return redirect('main:admin_inbox')

@user_passes_test(lambda u: u.is_superuser)
def admin_inbox_message_mark_unread(request, msg_id):
    message = get_object_or_404(ContactMessage, id=msg_id)
    messages.success(request, _('Contact message marked as unread'))
    message.state = 0
    message.save()
    return redirect('main:admin_inbox')

@user_passes_test(lambda u: u.is_superuser)
def admin_users_view(request):
    u_filter = UserFilter(request.GET, queryset=User.objects.all())
    table = UserTable(data=u_filter.qs, current_user=request.user)
    RequestConfig(request).configure(table)

    return render(request, 'main/admin/admin_users.html', {'table': table, 'filter': u_filter})


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

    data_source_type = serializers.serialize("json", SourceType.objects.all())
    zip_file.writestr("SourceType.json", data_source_type)

    data_author = serializers.serialize("json", Author.objects.all())
    zip_file.writestr("Scribe.json", data_author)

    data_documents = serializers.serialize("json", Document.objects.all())
    zip_file.writestr("Document.json", data_documents)

    data_institutions = serializers.serialize("json", Institution.objects.all())
    zip_file.writestr("Institution.json", data_institutions)

    data_ref_numbers = serializers.serialize("json", RefNumber.objects.all())
    zip_file.writestr("RefNumber.json", data_ref_numbers)

    zip_file.close()

    response = HttpResponse(open(file_name, 'rb'), content_type="application/zip")
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    os.remove(file_name)
    return response


def send_newsletter_view(request):
    form = SendNewsletterForm()
    return render(request, 'main/admin/send_newsletter.html', context={"form": form})



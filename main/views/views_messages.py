from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from main.forms.forms_user import UserMessageOptionsForm, WriteMessageForm
from main.tables import UserMessageTable
from main.models import User, UserMessage


@login_required
def messages_view(request):
    table = UserMessageTable(data=UserMessage.objects.filter(receiving_user=request.user))
    form = UserMessageOptionsForm()

    if request.method == 'POST':
        form = UserMessageOptionsForm(request.POST)

    return render(request, 'main/users/messages.html', {'table': table, 'form': form})


@login_required
def notifications_view(request):
    table = UserMessageTable(data=UserMessage.objects.filter(receiving_user=request.user))
    form = UserMessageOptionsForm()

    if request.method == 'POST':
        form = UserMessageOptionsForm(request.POST)

    return render(request, 'main/users/notifications.html', {'table': table, 'form': form})


@login_required
def delete_all_view(request):
    return HttpResponse('NIY')


@login_required
def message_user_view(request, username):
    receiving_user = User.objects.get(username=username)
    form = WriteMessageForm(user=receiving_user)

    if request.method == "POST":
        form = WriteMessageForm(request.POST, user=receiving_user)
        if form.is_valid():
            new_message = UserMessage.objects.create(sending_user=request.user,
                                                     receiving_user=receiving_user,
                                                     subject=form.cleaned_data['subject'],
                                                     message=form.cleaned_data['message'])
            messages.success(request, _('Your message has been sent.'))
            return redirect(request.META.get('HTTP_REFERER'))

    return render(request, 'main/users/write_message.html', {'form': form})


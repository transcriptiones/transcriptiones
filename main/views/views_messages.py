from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from main.forms.forms_user import UserMessageOptionsForm
from main.tables import UserMessageTable
from main.models import Document, RefNumber, User, UserSubscription, UserMessage


@login_required
def messages(request):
    table = UserMessageTable(data=UserMessage.objects.filter(user=request.user))
    form = UserMessageOptionsForm()

    if request.method == 'POST':
        form = UserMessageOptionsForm(request.POST)

    return render(request, 'main/users/messages.html', {'table': table, 'form': form})


@login_required
def delete_all_view(request):
    return HttpResponse('NIY')


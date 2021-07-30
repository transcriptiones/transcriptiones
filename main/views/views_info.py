from django.shortcuts import render

from main.forms.forms_info import ContactForm
from main.models import ContactMessage


def contact_view(request):
    form = ContactForm()

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(reply_email=form.cleaned_data['reply_to'],
                                          message=form.cleaned_data['message'])

    return render(request, 'main/info/contact.html', context={'form': form})

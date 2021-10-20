from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from main.mail_utils import send_contact_message_copy
from main.forms.forms_info import ContactForm, NewsletterSubscribeForm
from main.models import ContactMessage


def start_view(request):
    """Shows the main view"""
    form = NewsletterSubscribeForm()

    if request.method == "POST":
        form = NewsletterSubscribeForm(request.POST)

    return render(request, 'main/info/start.html', context={'form': form})


def contact_view(request):
    """Shows a view with a contact form to send a message to the transcriptiones team."""
    form = ContactForm()

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            new_message = ContactMessage.objects.create(reply_email=form.cleaned_data['reply_to'],
                                                        message=form.cleaned_data['message'])
            send_contact_message_copy(new_message)
            messages.success(request, _('Your Message has been sent. You received a copy by email.'))
            return redirect('main:about')

    return render(request, 'main/info/contact.html', context={'form': form})

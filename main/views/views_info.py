from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from main.mail_utils import send_contact_message_copy, send_newsletter_subscribe_mail
from main.forms.forms_info import ContactForm, NewsletterSubscribeForm, NewsletterUnsubscribeForm
from main.models import ContactMessage, NewsletterRecipients
from django.utils.translation import activate
from django.utils import translation

from transcriptiones import settings


def set_language_view(request, language):
    translation.activate(language)
    request.LANGUAGE_CODE = language

    redirect_url = request.META.get('HTTP_REFERER')
    if redirect_url is None:
        redirect_url = reverse('main:start')

    response = HttpResponseRedirect(redirect_url)

    if hasattr(request, 'session'):
        request.session['django_language'] = language
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)

    return response


def start_view(request):
    """Shows the main view"""
    form = NewsletterSubscribeForm()

    if request.method == "POST":
        form = NewsletterSubscribeForm(request.POST)
        if form.is_valid():
            if NewsletterRecipients.objects.filter(email_address=form.cleaned_data['email_address']).count() == 0:
                NewsletterRecipients.objects.create(email_address=form.cleaned_data['email_address'],
                                                    language=request.LANGUAGE_CODE)
                send_newsletter_subscribe_mail(request, form.cleaned_data['email_address'])
                messages.success(request, _('Thank you! You will receive our next newsletter.'))
                form = NewsletterSubscribeForm()
            else:
                messages.warning(request, _('Your address is already in our list.'))
        else:
            messages.error(request, _('Please fill in a valid email address.'))

    return render(request, 'main/info/start.html', context={'form': form})


def unsubsribe_newsletter_view(request):
    form = NewsletterUnsubscribeForm()

    if request.method == "POST":
        form = NewsletterUnsubscribeForm(request.POST)
        if form.is_valid():
            try:
                subscription = NewsletterRecipients.objects.get(email_address=form.cleaned_data['email_address'])
                subscription.delete()
                messages.success(request, _('You have been unsubscribed.'))
                return redirect('main:start')
            except NewsletterRecipients.DoesNotExist:
                messages.error(request, _("This address is not in our newsletter list."))

    return render(request, 'main/info/unsubscribe.html', context={'form': form})


def contact_view(request):
    """Shows a view with a contact form to send a message to the transcriptiones team."""
    form = ContactForm()

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            new_message = ContactMessage.objects.create(reply_email=form.cleaned_data['reply_to'],
                                                        subject=form.cleaned_data['subject'],
                                                        message=form.cleaned_data['message'])
            send_contact_message_copy(request, new_message)
            messages.success(request, _('Your Message has been sent. You received a copy by email.'))
            return redirect('main:about')

    return render(request, 'main/info/contact.html', context={'form': form})

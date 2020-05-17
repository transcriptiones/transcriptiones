from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from transcripta.transcripts.models import User
from transcripta.transcripts.forms import SignUpForm
from transcripta.transcripts.tokens import account_activation_token

# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(**form.cleaned_data)
            current_site = get_current_site(request)
            subject = 'Bitte aktivieren Sie Ihren Transcriptiones-Account'
            message = render_to_string('users/accountactivationemail.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                })
            send_mail(subject, message, 'dominic.weber@librarylab.ethz.ch', [user.email])
            return redirect('account_activation_sent')

    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})


class AccountActivationSentView(TemplateView):
    template_name = 'users/accountactivationsent.html'

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.email_confirmed = True
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('start')
    else:
        return render(request, 'users/accountactivationinvalid.html')
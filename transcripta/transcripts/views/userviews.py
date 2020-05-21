from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from transcripta.transcripts.models import User
from transcripta.transcripts.forms import SignUpForm, LoginForm, CustomPasswordChangeForm, UserUpdateForm, CustomPasswordResetForm, CustomSetPasswordForm
from transcripta.transcripts.tokens import account_activation_token
from transcripta.settings import DEFAULT_FROM_EMAIL

# View for display and handling of SignUpForm.
# Sends Link to confirm email

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(**form.cleaned_data)
            current_site = get_current_site(request)
            subject = 'Transcriptiones: Bitte aktivieren Sie Ihren Account'
            message = render_to_string('users/accountactivationemail.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                })
            send_mail(subject, message, DEFAULT_FROM_EMAIL, [user.email])
            return redirect('account_activation_sent')

    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})


# View to Inform the User that the confirmation-link has been sent.

class AccountActivationSentView(TemplateView):
    template_name = 'users/accountactivationsent.html'


# View to check token from confirmation-link. Logs User in and redirects to start

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


# View for Login

class CustomLoginView(LoginView):
    template_name = "users/login.html"
    form_class = LoginForm

# View for changing password
class CustomPasswordChangeView(PasswordChangeView):
    template_name = "users/passwordchange.html"
    form_class = CustomPasswordChangeForm

# View for User Profile Page
@login_required
def userprofile(request):
    user = request.user
    return render(request, 'users/userprofile.html', {'user': user})

# View for changing User Data
class UserUpdateView(LoginRequiredMixin, View):
    form_class = UserUpdateForm
    template_name = "users/updateuser.html"

    # display bound form if accessed via GET
    def get(self, *args, **kwargs):
        if self.request.method == "GET":
            user = self.request.user
            form = self.form_class(instance=user)

            return render(self.request, self.template_name, {'form': form})

    # validate form data and update user if accessed via POST.
    # Redirect to profile on success, else return template with errors
    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            user = self.request.user
            form = self.form_class(instance=user, data=self.request.POST)
            if form.is_valid():
                form.save()
                return redirect('profile')
            else:
                return render(self.request, self.template_name, {'form': form})

                
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    email_template_name = "users/passwordresetemail.html"
    subject_template_name = "users/passwordresetsubject.txt"
    template_name = "users/passwordreset.html"

class CustomPasswordConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = "users/passwordresetconfirm.html"
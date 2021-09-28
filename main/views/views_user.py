from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, TemplateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django_tables2 import RequestConfig

from transcriptiones.settings import DEFAULT_FROM_EMAIL

from main.models import User, UserSubscription
from main.forms.forms_user import SignUpForm, LoginForm, CustomPasswordChangeForm, UserUpdateForm, CustomPasswordResetForm, CustomSetPasswordForm
from main.tokens import account_activation_token
from main.model_info import get_user_info, get_public_user_info
from main.tables.tables_base import TitleValueTable
from main.tables.tables_document import DocumentUserHistoryTable
from main.filters import DocumentFilter


def signup(request):
    """View for display and handling of SignUpForm.
    Sends Link to confirm email"""

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(**form.cleaned_data)
            current_site = get_current_site(request)
            subject = 'Transcriptiones: Bitte aktivieren Sie Ihren Account'
            message = render_to_string('main/users/accountactivationemail.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                })
            send_mail(subject, message, DEFAULT_FROM_EMAIL, [user.email])
            return redirect('account_activation_sent')

    else:
        form = SignUpForm()
    return render(request, 'main/users/signup.html', {'form': form})


class AccountActivationSentView(TemplateView):
    """View to Inform the User that the confirmation-link has been sent."""
    template_name = 'main/users/account_activation_sent.html'


def activate(request, uidb64, token):
    """View to check token from confirmation-link. Logs User in and redirects to start"""

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
        return render(request, 'main/users/account_activation_invalid.html')


class CustomLoginView(SuccessMessageMixin, LoginView):
    """View for Login"""
    template_name = "main/users/login.html"
    form_class = LoginForm
    success_message = _('Successfully logged in!')


class CustomPasswordChangeView(PasswordChangeView):
    """View for changing password"""
    template_name = "main/users/password_change.html"
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('main:password_change_done')


@login_required
def userprofile(request):
    """View for User Profile Page"""
    contributions = request.user.contributions(manager='all_objects').all().order_by('-document_utc_add')
    paginator = Paginator(contributions, 10)

    page_number = request.GET.get('page')
    contributions_pg = paginator.get_page(page_number)

    user_table = TitleValueTable(data=get_user_info(request.user))

    d_filter = DocumentFilter(request.GET, queryset=contributions)
    activity_table = DocumentUserHistoryTable(data=d_filter.qs)
    RequestConfig(request).configure(activity_table)

    return render(request, 'main/users/user_profile.html', {'user_table': user_table, 'activity_table': activity_table, 'filter': d_filter})


@login_required
def my_documents(request):
    """View for User Documents"""
    contributions = request.user.contributions(manager='all_objects').all().order_by('-document_utc_add')
    paginator = Paginator(contributions, 10)

    page_number = request.GET.get('page')

    d_filter = DocumentFilter(request.GET, queryset=contributions)
    activity_table = DocumentUserHistoryTable(data=d_filter.qs)
    RequestConfig(request).configure(activity_table)

    return render(request, 'main/users/my_documents.html', {'activity_table': activity_table, 'filter': d_filter})

@login_required
def public_profile(request, username):
    """View for Public User Profile Page"""
    user = User.objects.get(username=username)
    contributions = user.contributions(manager='all_objects').filter(publish_user=True).order_by('-document_utc_add')

    user_table = TitleValueTable(data=get_public_user_info(user))

    d_filter = DocumentFilter(request.GET, queryset=contributions)
    activity_table = DocumentUserHistoryTable(data=d_filter.qs)
    RequestConfig(request).configure(activity_table)

    subscribed = UserSubscription.objects.filter(user=request.user,
                                                 subscription_type=UserSubscription.SubscriptionType.USER,
                                                 object_id=user.id).count() > 0
    return render(request, 'main/users/public_user_profile.html', {'profile_user': user,
                                                                   'user_table': user_table,
                                                                   'activity_table': activity_table,
                                                                   'filter': d_filter,
                                                                   'subscribed': subscribed})


class UserUpdateView(LoginRequiredMixin, View):
    """View for changing User Data"""

    form_class = UserUpdateForm
    template_name = "main/users/update_user.html"

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
    email_template_name = "main/users/password_reset_email.html"
    subject_template_name = "main/users/password_reset_subject.txt"
    template_name = "main/users/password_reset.html"
    success_url = reverse_lazy('main:password_reset_done')


class CustomPasswordConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = "main/users/password_reset_confirm.html"
    success_url = reverse_lazy('main:password_reset_complete')

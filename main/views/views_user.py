import hashlib
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.contrib import messages
from django.contrib.auth.models import Permission
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, TemplateView
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator
from django_tables2 import RequestConfig

from main.mail_utils import send_registration_confirmation_mail, send_username_request_mail, send_changed_address_mail

from main.models import User, UserSubscription
from main.forms.forms_user import SignUpForm, LoginForm, CustomPasswordChangeForm, UserUpdateForm, \
    CustomPasswordResetForm, CustomSetPasswordForm, RequestUsernameForm, ChangeEmailForm
from main.tokens import account_activation_token
from main.model_info import get_user_info, get_public_user_info
from main.tables.tables_base import TitleValueTable
from main.tables.tables_document import DocumentUserHistoryTable
from main.filters import DocumentFilter
from main.views.views_browse import get_document_filter_data


def signup(request):
    """View for display and handling of SignUpForm.
    Sends Link to confirm email"""

    form = SignUpForm(initial={'ui_language': request.LANGUAGE_CODE})

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # remove field tos_accepted from form data to prevent ValueError
            form.cleaned_data.pop('tos_accepted')
            user = User.objects.create_user(**form.cleaned_data)
            send_registration_confirmation_mail(request, user)
            return redirect('main:account_activation_sent')

    return render(request, 'main/users/signup.html', {'form': form})


class AccountActivationSentView(TemplateView):
    """View to Inform the User that the confirmation-link has been sent."""
    template_name = 'main/users/account_activation_sent.html'


def show_activation_page(request, uidb64, token):
    return render(request, 'main/users/email_templates/activate_account.html', context={"uid": uidb64, "token": token})


def activate(request):
    """View to check token from confirmation-link. Logs User in and redirects to the start page"""

    if request.method == "POST":
        uidb64 = request.POST.get("uid", None)
        token = request.POST.get("token", None)

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.email_confirmed = True
            user.is_active = True
            permission = Permission.objects.get(codename='add_author')
            user.user_permissions.add(permission)
            user.save()
            login(request, user)
            messages.success(request, _('Successfully logged in!'))
            return redirect('main:start')

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

    user_table = TitleValueTable(data=get_user_info(request.user))

    return render(request, 'main/users/user_profile.html', {'user_table': user_table})


@login_required
def my_documents(request):
    """View for User Documents"""
    contributions = request.user.contributions(manager='all_objects').all().order_by('-document_utc_add')
    paginator = Paginator(contributions, 10)

    page_number = request.GET.get('page')

    d_filter = DocumentFilter(request.GET, queryset=contributions)
    activity_table = DocumentUserHistoryTable(data=d_filter.qs)
    RequestConfig(request).configure(activity_table)

    return render(request, 'main/users/my_documents.html', {'activity_table': activity_table,
                                                            'form_data': get_document_filter_data(request, d_filter),
                                                            'filter': d_filter, # Dont need anymore
                                                            })


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
                                                                   'subscribed': subscribed,
                                                                   'form_data': get_document_filter_data(request, d_filter)})


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
                messages.success(self.request, _('Your user information has been updated'))
                return redirect('main:profile')
            else:
                return render(self.request, self.template_name, {'form': form})

                
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    email_template_name = "main/users/email_templates/password_reset_email.html"
    subject_template_name = "main/users/email_templates/password_reset_subject.txt"
    template_name = "main/users/password_reset.html"
    success_url = reverse_lazy('main:password_reset_done')


class CustomPasswordConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = "main/users/password_reset_confirm.html"
    success_url = reverse_lazy('main:password_reset_complete')


def request_username_view(request):
    """A user might forget his username which he logged in with. He can request it over this for"""

    if request.method == 'POST':
        form = RequestUsernameForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email=form.cleaned_data['email_of_user'])
                send_username_request_mail(request, user)
                return redirect('main:username_request_done')
            except User.DoesNotExist:
                messages.error(_('This email address is not registered.'))
    else:
        form = RequestUsernameForm()
    return render(request, 'main/users/request_username.html', {'form': form})


def request_username_done_view(request):
    return render(request, 'main/users/request_username_done.html')


@login_required()
def change_email_view(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            try:
                existing_users_with_this_email = User.objects.get(email=form.cleaned_data['new_email_of_user'])
                messages.error(request, _('This address is already in use!'))
            except User.DoesNotExist:
                request.user.email = form.cleaned_data['new_email_of_user']
                request.user.save()
                send_changed_address_mail(request, request.user)
                return redirect('main:change_email_request_done')

    else:
        form = ChangeEmailForm({"new_email_of_user": request.user.email})

    return render(request, 'main/users/change_email.html', context={"form": form})


def request_email_change_done_view(request):
    user = request.user
    logout(request)
    return render(request, 'main/users/change_email_done.html', context={'logged_out_user': user})


@login_required
def generate_api_secret(request):
    secret_string = request.user.username + str(request.user.id) + "This%&Isç%A+Secretç%String1209385btr"
    request.user.api_auth_key = hashlib.md5(secret_string.encode('utf-8')).hexdigest()
    request.user.api_auth_key_expiration = datetime.today() + relativedelta(months=1)
    request.user.save()
    messages.success(request, _("An API Key has been generated"))
    return redirect('main:profile')


@login_required
def renew_api_secret(request):
    if request.user.api_auth_key is None:
        messages.error(request, _("You need to generate an API key first."))
        return redirect('main:profile')

    current_date = datetime.today()
    expiration_date = current_date + relativedelta(months=1)
    request.user.api_auth_key_expiration = expiration_date
    request.user.save()
    messages.success(request, _("Your API Key has been renewed"))
    return redirect('main:profile')

@login_required
def delete_api_secret(request):
    if request.user.api_auth_key is None:
        messages.error(request, _("No API key was found to delete."))
        return redirect('main:profile')

    request.user.api_auth_key = None
    request.user.save()

    messages.success(request, _("Your API Key has been deleted"))
    return redirect('main:profile')

"""Contains all the tables for the transcriptiones app."""
import django_tables2 as tables
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from django_tables2 import A
from main.models import RefNumber, Document, Institution, UserSubscription, User, UserMessage, UserNotification, \
    ContactMessage, SourceType, Author
from main.tables.tables_base import TranscriptionesTable, default_table_attrs, default_row_attrs


class UserTable(TranscriptionesTable):
    """The UserTable shows a list of users. It features the user's state (active/inactive | user/staff/admin) and
    displays options to activate/deactivate users and change their privileges."""

    def __init__(self, *args, **kwargs):
        temp_user = kwargs.pop("current_user", None)
        super(UserTable, self).__init__(*args, **kwargs)
        self.current_user = temp_user

    class Meta(TranscriptionesTable.Meta):
        model = User
        fields = ("username", )

    username = tables.LinkColumn('main:public_profile', args=[A('username')])
    state = tables.Column(accessor='id', verbose_name=_("User State"), orderable=False)
    options = tables.Column(accessor='id', verbose_name=_("Options"), orderable=False)

    @staticmethod
    def render_state(value, record):
        activity_state = record.get_user_activity_badge()
        user_state = record.get_user_state_badge()

        return mark_safe(activity_state + "&nbsp;" + user_state)

    def render_options(self, value, record):
        # No options for the logged in user. He cannot deactivate himself
        if record.id == self.current_user.id:
            return ''

        # Options only for active users: else only activate
        options = ''
        if record.is_active:
            # A user can not be deactivated if she is a superuser
            if not record.is_superuser or self.current_user.username == "admin":
                deactivate_title = _("Deactivate this user")
                deactivate_url = reverse('main:admin_deactivate_user', kwargs={'user_id': record.id})
                options += f'<a href="{deactivate_url}" class="btn btn-sm btn-danger confirm-deactivate" title="{deactivate_title}" data-toggle="modal" data-target="#confirmDeactivateModal" id="deactivateButton{record.id}"><i class="fas fa-toggle-off"></i></a> &nbsp;'

            make_staff_title = _("Make this user staff")
            make_staff_url = reverse('main:admin_set_user_staff', kwargs={'user_id': record.id})
            if not record.is_staff:
                options += f'<a href="{make_staff_url}" class="btn btn-sm btn-warning" title="{make_staff_title}"><i class="fas fa-users-cog"></i></a> &nbsp;'
            if record.is_staff and not record.is_superuser and self.current_user.is_superuser:
                make_admin_title = _("Make this user an administrator")
                make_user_title = _("Make this user a normal user")
                make_admin_url = reverse('main:admin_set_user_admin', kwargs={'user_id': record.id})
                make_user_url = reverse('main:admin_set_user_user', kwargs={'user_id': record.id})
                options += f'<a href="{make_user_url}" class="btn btn-sm btn-primary" title="{make_user_title}"><i class="fas fa-user"></i></a> &nbsp;'
                options += f'<a href="{make_admin_url}" class="btn btn-sm btn-danger" title="{make_admin_title}"><i class="fas fa-user-shield"></i></a> &nbsp;'
            # Only the superuser named admin can downgrade other users
            if record.is_superuser and self.current_user.username == 'admin':
                options += f'<a href="{make_staff_url}" class="btn btn-sm btn-warning" title="{make_staff_title}"><i class="fas fa-users-cog"></i></a> &nbsp;'

        # User is inactive
        else:
            activate_title = _("Activate this user")
            activate_url = reverse('main:admin_activate_user', kwargs={'user_id': record.id})
            options = f'<a href="{activate_url}" class="btn btn-sm btn-primary" title="{activate_title}"><i class="fas fa-toggle-on"></i></a>'

        """make_staff_url = reverse('main:admin_set_user_staff', kwargs={'user_id': record.id})
        make_user_url = reverse('main:admin_set_user_user', kwargs={'user_id': record.id})
        message_url = reverse('main:message_user', kwargs={'username': record.username})"""

        return mark_safe(options)


class ContactMessageTable(TranscriptionesTable):
    """The ContactMessageTable shows a list contact messages."""

    class Meta(TranscriptionesTable.Meta):
        model = ContactMessage
        fields = ("state", "reply_email", "subject", "sending_time")

    state = tables.Column(verbose_name=_('Answered'), orderable=False)
    reply_email = tables.Column(verbose_name=_('from'), orderable=False)
    subject = tables.LinkColumn('main:admin_inbox_message', args=[A('pk')], orderable=False)
    sending_time = tables.Column(verbose_name=_('sent'), orderable=False)

    @staticmethod
    def render_reply_email(value, record):
        if record.state == 0:
            return mark_safe(f"<strong>{value}</strong>")
        return value

    @staticmethod
    def render_subject(value, record):
        if record.state == 0:
            return mark_safe(f"<strong>{value}</strong>")
        return value

    @staticmethod
    def render_sending_time(value, record):
        if record.state == 0:
            return mark_safe(f'<strong>{value.strftime("%b %d %Y %H:%M:%S")}</strong>')
        return value.strftime("%b %d %Y %H:%M:%S")

    @staticmethod
    def render_state(value, record):
        if value == 0:
            return mark_safe(f'<span style="color: red;">&cross;</span><a class="btn-sm btn-danger" href="{reverse("main:admin_inbox_message_mark_spam", kwargs={"msg_id": record.id})}">{_("Mark Spam")}</a>')
        if record.state == 2:
            return _("Marked Spam")
        return mark_safe(f'<span style="color: green;">&check;</span>')


class UserNotificationTable(tables.Table):
    """The UserMessageTable shows a list of subscriptions to ref numbers, documents or users."""

    class Meta:
        model = UserNotification
        template_name = "django_tables2/bootstrap4-responsive.html"
        fields = ("subject", "message", "sending_time")
        attrs = {"class": "table table-hover",
                 'td': {'style': 'text-align: left;'}
                 }

    message = tables.TemplateColumn(
        '<data-toggle="tooltip" title="{{record.message}}">{{record.message|truncatewords:5}}')


class UserMessageTable(TranscriptionesTable):
    """The UserMessageTable shows a list of messages, notifications and contact-messages."""

    sending_user = tables.Column(verbose_name=_('From'), orderable=False)
    subject = tables.LinkColumn('main:messages_read', args=[A('message_type'), A('pk')], verbose_name=_('Subject'),
                                orderable=False)
    sending_time = tables.Column(verbose_name=_('Sent At'), orderable=False)

    class Meta(TranscriptionesTable.Meta):
        pass

    @staticmethod
    def render_sending_user(value, record):
        if record['viewing_state'] == 0:
            return mark_safe(f"<strong>{value}</strong>")
        return value

    @staticmethod
    def render_subject(value, record):
        if record['viewing_state'] == 0:
            return mark_safe(f"<strong>{value}</strong>")
        return value

    @staticmethod
    def render_sending_time(value, record):
        if record['viewing_state'] == 0:
            return mark_safe(f'<strong>{value.strftime("%b %d %Y %H:%M:%S")}</strong>')
        return value.strftime("%b %d %Y %H:%M:%S")


class UserSubscriptionTable(tables.Table):
    """The UserSubscriptionTable shows a list of subscriptions to ref numbers, documents or users."""

    class Meta:
        model = UserSubscription
        template_name = "django_tables2/bootstrap4-responsive.html"
        fields = ("subscription_type", "object_id",)
        attrs = {"class": "table table-hover",
                 'td': {'style': 'text-align: left;'}
                 }

    subscription_type = tables.Column(orderable=False)
    object_id = tables.Column(orderable=False, verbose_name=_('Subscription object'))
    options = tables.Column(orderable=False, accessor='id', verbose_name=_('Options'))

    @staticmethod
    def render_subscription_type(value, record):
        badge_class = "secondary"
        if value == UserSubscription.SubscriptionType.USER.label:
            badge_class = "success"
        if value == UserSubscription.SubscriptionType.REF_NUMBER.label:
            badge_class = "warning"
        if value == UserSubscription.SubscriptionType.DOCUMENT.label:
            badge_class = "info"
        if value == UserSubscription.SubscriptionType.INSTITUTION.label:
            badge_class = "dark"

        return mark_safe(f'<span class="badge badge-{badge_class}">{value}</span>')

    @staticmethod
    def render_object_id(value, record):
        if record.subscription_type == UserSubscription.SubscriptionType.REF_NUMBER:
            ref_number = RefNumber.objects.get(id=value)
            return ref_number.ref_number_name + ": " + ref_number.ref_number_title
        if record.subscription_type == UserSubscription.SubscriptionType.DOCUMENT:
            document = Document.all_objects.get(id=value)
            return document.title_name
        if record.subscription_type == UserSubscription.SubscriptionType.INSTITUTION:
            institution = Institution.objects.get(id=value)
            return institution.institution_name
        if record.subscription_type == UserSubscription.SubscriptionType.AUTHOR:
            author = Author.objects.get(id=value)
            return author.author_name
        if record.subscription_type == UserSubscription.SubscriptionType.USER:
            user = User.objects.get(id=value)
            return user.username
        return value

    @staticmethod
    def render_options(value, record):
        url = '#'
        url_view = '#'
        if record.subscription_type == UserSubscription.SubscriptionType.REF_NUMBER:
            url = reverse('main:unsubscribe_ref_number', kwargs={'pk': record.object_id})
            ref_number = RefNumber.objects.get(id=record.object_id)
            url_view = reverse('main:ref_number_detail',
                               kwargs={'inst_slug': ref_number.holding_institution.institution_slug,
                                       'ref_slug': ref_number.ref_number_slug})

        if record.subscription_type == UserSubscription.SubscriptionType.DOCUMENT:
            url = reverse('main:unsubscribe_document', kwargs={'pk': record.object_id})
            document = Document.all_objects.get(id=record.object_id)
            url_view = reverse('main:document_detail',
                               kwargs={'inst_slug': document.parent_ref_number.holding_institution.institution_slug,
                                       'ref_slug': document.parent_ref_number.ref_number_slug,
                                       'doc_slug': document.document_slug})

        if record.subscription_type == UserSubscription.SubscriptionType.USER:
            url = reverse('main:unsubscribe_user', kwargs={'pk': record.object_id})
            user = User.objects.get(id=record.object_id)
            url_view = reverse('main:public_profile', kwargs={'username': user.username})

        if record.subscription_type == UserSubscription.SubscriptionType.INSTITUTION:
            url = reverse('main:unsubscribe_institution', kwargs={'pk': record.object_id})
            institution = Institution.objects.get(id=record.object_id)
            url_view = reverse('main:institution_detail', kwargs={'inst_slug': institution.institution_slug})

        html_text = format_lazy('<a class="btn btn-danger btn-sm" href="{url}" role="button">{unsubscribe}</a> &nbsp;' \
                                '<a class="btn btn-primary btn-sm" href="{url_view}" role="button">{view}</a>',
                                url=url, url_view=url_view, unsubscribe=_('Unsubscribe'), view=_('View'))

        return mark_safe(html_text)









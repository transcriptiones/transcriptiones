"""Contains all the tables for the transcriptiones app."""
import django_tables2 as tables
import django.utils.html as utils
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django_tables2 import A

from main.models import RefNumber, Document, Institution, UserSubscription, User, UserMessage, UserNotification, \
    ContactMessage, SourceType, Author
from main.tables.tables_base import TranscriptionesTable, default_table_attrs, default_row_attrs


class UserTable(TranscriptionesTable):
    """The UserTable shows a list of users. It features the user's state (active/inactive | user/staff/admin) and displays options to
    activate/deactivate users and change their privileges."""

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

    def render_state(self, value, record):
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

        make_staff_url = reverse('main:admin_set_user_staff', kwargs={'user_id': record.id})
        make_user_url = reverse('main:admin_set_user_user', kwargs={'user_id': record.id})
        message_url = reverse('main:message_user', kwargs={'username': record.username})

        return mark_safe(options)


class ContactMessageTable(tables.Table):
    """The UserMessageTable shows a list of subscriptions to ref numbers, documents or users."""

    class Meta:
        model = ContactMessage
        template_name = "django_tables2/bootstrap4.html"
        fields = ("sending_user", "subject", "sending_time")
        attrs = {"class": "table table-hover",
                 'td': {'style': 'text-align: left;'}
                 }

    reply_email = tables.Column(verbose_name='from', orderable=False)
    subject = tables.LinkColumn('main:contact_message_read', args=[A('pk')], orderable=False)
    sending_time = tables.Column(verbose_name='sent', orderable=False)
    options = tables.Column(accessor='id', verbose_name="", orderable=False)


class UserNotificationTable(tables.Table):
    """The UserMessageTable shows a list of subscriptions to ref numbers, documents or users."""

    class Meta:
        model = UserNotification
        template_name = "django_tables2/bootstrap4.html"
        fields = ("subject", "message", "sending_time")
        attrs = {"class": "table table-hover",
                 'td': {'style': 'text-align: left;'}
                 }

    message = tables.TemplateColumn(
        '<data-toggle="tooltip" title="{{record.message}}">{{record.message|truncatewords:5}}')


class UserMessageTable(tables.Table):
    """The UserMessageTable shows a list of subscriptions to ref numbers, documents or users."""

    class Meta:
        model = UserMessage
        template_name = "django_tables2/bootstrap4.html"
        fields = ("sending_user", "subject", "sending_time")
        attrs = {"class": "table table-hover",
                 'td': {'style': 'text-align: left;'}
                 }

    sending_user = tables.Column(verbose_name='from', orderable=False)
    subject = tables.LinkColumn('main:messages_read', args=[A('pk')], orderable=False)
    sending_time = tables.Column(verbose_name='sent', orderable=False)
    options = tables.Column(accessor='id', verbose_name="", orderable=False)

    """
    message = tables.TemplateColumn(
        '<data-toggle="tooltip" title="{{record.message}}">{{record.message|truncatewords:5}}')
    """

    def render_sending_user(self, value, record):
        if record.viewing_state == 0:
            return mark_safe(f"<strong>{value}</strong>")
        return value

    def render_subject(self, value, record):
        if record.viewing_state == 0:
            return mark_safe(f"<strong>{value}</strong>")
        return value

    def render_sending_time(self, value, record):
        if record.viewing_state == 0:
            return mark_safe(f'<strong>{value.strftime("%b %d %Y %H:%M:%S")}</strong>')
        return value.strftime("%b %d %Y %H:%M:%S")

    def render_options(self, value, record):
        open_url = reverse('main:messages_read', kwargs={'message_id': record.id})
        reply_url = reverse('main:messages_reply', kwargs={'message_id': record.id})
        delete_url = reverse('main:messages_delete', kwargs={'message_id': record.id})

        open_title = _("Open this message")
        reply_title = _("Reply to this message")
        delete_title = _("Delete this message")

        options = f'<a href="{delete_url}" class="confirm-delete" title="Delete" data-toggle="modal" data-target="#confirmDeleteModal" id="deleteButton{record.id}">Delete</a>'
        """
        options += f'<a href="{open_url}" class="btn btn-sm btn-primary" title="{open_title}"><i class="fas fa-envelope-open"></i></a> &nbsp;'
        options += f'<a href="{reply_url}" class="btn btn-sm btn-primary" title="{reply_title}"><i class="fas fa-reply"></i></a> &nbsp;'
        options += f'<a href="{delete_url}" class="btn btn-sm btn-danger" title="{delete_title}"><i class="fas fa-trash"></i></a> &nbsp;'
        """
        return mark_safe(options)


class UserSubscriptionTable(tables.Table):
    """The UserSubscriptionTable shows a list of subscriptions to ref numbers, documents or users."""

    class Meta:
        model = UserSubscription
        template_name = "django_tables2/bootstrap4.html"
        fields = ("subscription_type", "object_id",)
        attrs = {"class": "table table-hover",
                 'td': {'style': 'text-align: left;'}
                 }

    subscription_type = tables.Column(orderable=False)
    object_id = tables.Column(orderable=False, verbose_name=_('Subscription object'))
    options = tables.Column(orderable=False, accessor='id', verbose_name=_('Options'))

    def render_subscription_type(self, value, record):
        badge_class = "secondary"
        if value == UserSubscription.SubscriptionType.USER.label:
            badge_class = "success"
        if value == UserSubscription.SubscriptionType.REF_NUMBER.label:
            badge_class = "warning"
        if value == UserSubscription.SubscriptionType.DOCUMENT.label:
            badge_class = "info"

        return mark_safe(f'<span class="badge badge-{badge_class}">{value}</span>')

    def render_object_id(self, value, record):
        if record.subscription_type == UserSubscription.SubscriptionType.REF_NUMBER:
            ref_number = RefNumber.objects.get(id=value)
            return ref_number.ref_number_name + ": " + ref_number.ref_number_title
        if record.subscription_type == UserSubscription.SubscriptionType.DOCUMENT:
            document = Document.objects.get(id=value)
            return document.title_name
        if record.subscription_type == UserSubscription.SubscriptionType.USER:
            user = User.objects.get(id=value)
            return user.username
        return value

    def render_options(self, value, record):
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
            document = Document.objects.get(id=record.object_id)
            url_view = reverse('main:document_detail',
                               kwargs={'inst_slug': document.parent_ref_number.holding_institution.institution_slug,
                                       'ref_slug': document.parent_ref_number.ref_number_slug,
                                       'doc_slug': document.document_slug})

        if record.subscription_type == UserSubscription.SubscriptionType.USER:
            url = reverse('main:unsubscribe_user', kwargs={'pk': record.object_id})
            user = User.objects.get(id=record.object_id)
            url_view = reverse('main:public_profile', kwargs={'username': user.username})

        html_text = f'<a class="btn btn-danger btn-sm" href="{url}" role="button">Unsubscribe</a> &nbsp;' \
                    f'<a class="btn btn-primary btn-sm" href="{url_view}" role="button">View</a>'
        return mark_safe(html_text)









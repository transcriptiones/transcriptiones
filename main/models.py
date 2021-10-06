import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from partial_date import PartialDateField
from django_countries.fields import CountryField
from languages_plus.models import Language
from ckeditor.fields import RichTextField
from rest_framework import serializers


class Institution(models.Model):
    """An institution is a physical location which holds documents. These documents have a reference number.
    Reference numbers are always associated with an institution."""

    institution_name = models.CharField(verbose_name=_("Institution"),
                                        max_length=80,
                                        unique=True,
                                        help_text=_("Complete name of the institution"))

    street = models.CharField(verbose_name=_("Street"),
                              max_length=80,
                              help_text=_("Street with number"))

    zip_code = models.IntegerField(verbose_name=_("Zip code"),
                                   help_text=_("Zip code"))

    city = models.CharField(verbose_name=_("City"),
                            max_length=100,
                            help_text=_("City"))

    country = CountryField(verbose_name=_("Country"),
                           help_text=_("Country"))

    site_url = models.URLField(verbose_name=_("Web site"),
                               max_length=200,
                               blank=True,
                               help_text=_("URL of the web site"))

    institution_utc_add = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   verbose_name=_("Created by"),
                                   on_delete=models.PROTECT,  # Users are not supposed to be deletable
                                   related_name="institution_creator")

    last_update_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                       verbose_name=_("Updated by"),
                                       on_delete=models.PROTECT,  # Users are not supposed to be deletable
                                       related_name="institution_updater",
                                       blank=True, null=True,
                                       default=None)

    institution_slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institutions")

    def __str__(self):
        return self.institution_name

    def get_absolute_url(self):
        return reverse('main:institution_detail', kwargs={'inst_slug': self.institution_slug})


class RefNumber(models.Model):
    """Physical Collections are identified by a reference number (RefNumber). These collections can contain multiple
    documents with multiple pages."""

    holding_institution = models.ForeignKey(Institution,
                                            verbose_name=_("Institution"),
                                            on_delete=models.PROTECT,
                                            help_text=_("Institution associated with this reference number"))

    ref_number_name = models.CharField(verbose_name=_("Reference number"),
                                       max_length=100,
                                       help_text=_("reference number of the collection containing a document"))

    ref_number_title = models.CharField(verbose_name=_("Title"),
                                        max_length=150,
                                        blank=True,
                                        help_text=_("Title of the collection"))

    collection_link = models.URLField(verbose_name=_("Static URL"),
                                      max_length=200,
                                      blank=True,
                                      help_text=_("Link to the collection"))

    ref_number_utc_add = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   verbose_name=_("Created by"),
                                   on_delete=models.PROTECT,  # Users are not supposed to be deletable
                                   related_name="ref_number_creator")

    last_update_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                       verbose_name=_("Updated by"),
                                       on_delete=models.PROTECT,  # Users are not supposed to be deletable
                                       related_name="ref_number_updater",
                                       blank=True, null=True,
                                       default=None)

    ref_number_slug = models.SlugField(unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['ref_number_name', 'holding_institution'], name='unique_ref_number'),
        ]

        verbose_name = _("reference number")
        verbose_name_plural = _("reference numbers")

    def __str__(self):
        return self.ref_number_name

    def get_absolute_url(self):
        return reverse('main:ref_number_detail',
                       kwargs={'inst_slug': self.holding_institution.institution_slug, 'ref_slug': self.ref_number_slug})


class Author(models.Model):
    """Authors are people who wrote the **original** documents which were transcribed. They are **not** the
    transcribers of the documents."""

    author_name = models.CharField(verbose_name=_("Name of author"),
                                   max_length=150,
                                   help_text=_("Name of the author of the original document."))

    author_gnd = models.URLField(verbose_name=_("Link to GND entry"),
                                 max_length=100,
                                 blank=True,
                                 help_text=_("Persistent URL to the GND entry of the author."))

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   verbose_name=_("Created by"),
                                   on_delete=models.PROTECT,  # Users are not supposed to be deletable
                                   related_name="author_creator")

    last_update_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                       verbose_name=_("Updated by"),
                                       on_delete=models.PROTECT,  # Users are not supposed to be deletable
                                       related_name="author_updater",
                                       blank=True, null=True,
                                       default=None)

    class Meta:
        verbose_name = _("Document author")
        verbose_name_plural = _("Document authors")

    def get_absolute_url(self):
        return reverse('main:author_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.author_name


class SourceType(models.Model):
    """Type """
    type_name = models.CharField(verbose_name="archivalienart",
                                 max_length=50,)

    parent_type = models.ForeignKey('self',
                                    verbose_name="übergeordnete Archivalienart",
                                    on_delete=models.CASCADE,
                                    null=True,
                                    blank=True,
                                    related_name="child_type",)

    class Meta:
        verbose_name = _("Source type")
        verbose_name_plural = _("Source types")

    def get_absolute_url(self):
        return reverse('main:source_type_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.type_name


class DocumentManager(models.Manager):
    """This Manager returns the latest versions of documents."""
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class Document(models.Model):
    class MaterialType(models.IntegerChoices):
        PAPER = 1, _('Paper')
        PARCHMENT = 2, _('Parchment')
        PAPYRUS = 3, _('Papyrus')

        __empty__ = _('(Unknown)')

    class PaginationType(models.IntegerChoices):
        PAGES = 1, _('Pagination')
        FOILS = 2, _('Foliated')

        __empty__ = _('(Unknown)')

    document_id = models.UUIDField(verbose_name=_("Document UUID"),
                                   default=uuid.uuid1,
                                   editable=False,
                                   help_text=_("ID of the first Version of this document. Is kept constant between "
                                               "versions of this document."))

    title_name = models.CharField(verbose_name=_("Title"),
                                  max_length=200,
                                  help_text=_("Title of the Document"))

    parent_ref_number = models.ForeignKey(RefNumber,
                                          verbose_name=_("Reference Number"),
                                          on_delete=models.PROTECT,
                                          help_text="Reference number of the source")

    author = models.ManyToManyField(Author,
                                    verbose_name=_("Source Participants"),
                                    blank=True, null=True,
                                    help_text=_("Authors, Copiers, Editors"))

    doc_start_date = PartialDateField(verbose_name=_("Creation period start"),
                                      help_text=_("When was the document written? Be as specific as possible. <br/>"
                                                  "Valid fromats: YYYY ('1792'), MM.YYYY ('01.1980'), "
                                                  "DD.MM.YYYY ('23.07.1643')"))

    doc_end_date = PartialDateField(verbose_name=_("Creation period end"),
                                    null=True,
                                    blank=True,
                                    help_text=_("If the document was created over a time span, "
                                                "please indicate the end time. <br/>"
                                                "Valid fromats: YYYY ('1792'), MM.YYYY ('01.1980'), "
                                                "DD.MM.YYYY ('23.07.1643')"))

    place_name = models.CharField(verbose_name=_("Creation Location"),
                                  max_length=150,
                                  blank=False,
                                  help_text=_("The City/Place where the source was created."))

    language = models.ManyToManyField(Language,
                                      verbose_name=_("Languages"),
                                      blank=True, null=True,
                                      help_text=_("Languages used in the source"))

    source_type = models.ForeignKey(SourceType,
                                    verbose_name=_("Source Type"),
                                    on_delete=models.PROTECT,
                                    blank=False,
                                    null=False,
                                    help_text=_("Type of the source"))

    material = models.IntegerField(verbose_name=_("Writing material"),
                                   blank=True,
                                   null=True,
                                   choices=MaterialType.choices,
                                   help_text=_("Is the manuscript on paper, papyrus or parchment?"))

    measurements_length = models.DecimalField(verbose_name=_("Height"),
                                              max_digits=5,
                                              decimal_places=1,
                                              blank=True,
                                              null=True,
                                              help_text=_("Height in centimeters (cm)"))

    measurements_width = models.DecimalField(verbose_name=_("Width"),
                                             max_digits=5,
                                             decimal_places=1,
                                             blank=True,
                                             null=True,
                                             help_text=_("Width in centimeters (cm)"))

    pages = models.PositiveSmallIntegerField(verbose_name=_("Number of pages"),
                                             blank=True,
                                             null=True,
                                             help_text=_("The number of pages of the whole source"))

    paging_system = models.IntegerField(verbose_name=_("Pagination"),
                                        null=True,
                                        blank=True,
                                        choices=PaginationType.choices,
                                        help_text=_("How are the pages numbered?"))

    transcription_scope = models.TextField(verbose_name=_("Transcribed parts of the document"),
                                           help_text=_("List of the transcribed pages/chapters, etc."))

    comments = models.TextField(verbose_name=_("Editorial comments"),
                                blank=True,
                                help_text=_("Add editorial comments or remarks on the contents of the document."))

    transcription_text = RichTextField(verbose_name=_("Transcript"),
                                       help_text=_("Formatted text of your transcript."))

    document_utc_add = models.DateTimeField(verbose_name=_("Upload date"),
                                            auto_now_add=True)

    document_utc_update = models.DateTimeField(verbose_name=_("Update date"),
                                               auto_now=True)

    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     verbose_name=_("Submitted by"),
                                     on_delete=models.PROTECT,  # Users are not supposed to be deletable
                                     related_name="contributions",
                                     help_text=_("Uploading user"),
                                     editable=False)

    publish_user = models.BooleanField(verbose_name=_("Publish anonymous"),
                                       default=False,
                                       help_text=_("Select this, if you want to publish this document anonymously"))

    document_slug = models.SlugField()

    active = models.BooleanField(default=True, editable=False)  # Whether this is the latest version

    commit_message = models.CharField(verbose_name=_("Changes"),
                                      max_length=255,
                                      default="initial",
                                      help_text=_("A brief description of the applied changes."))

    version_number = models.IntegerField(verbose_name=_("version number"),
                                         default=1,
                                         help_text=_("Version number"))

    seal = models.BooleanField(verbose_name=_("Seal"),
                               blank=True,
                               null=True,
                               help_text=_("Are there any seals on this page?"))

    illuminated = models.BooleanField(verbose_name=_("Illuminations"),
                                      blank=True,
                                      null=True,
                                      help_text=_("Does the source contain painted miniatures (=illuminations)?"))

    objects = DocumentManager()  # Only current versions
    all_objects = models.Manager()  # Absolutely all objects, even outdated versions

    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("documents")
        default_manager_name = "objects"
        get_latest_by = "document_utc_add"
        constraints = [
            UniqueConstraint(fields=['document_slug'], condition=Q(active=True), name='unique_active_slug'),
            UniqueConstraint(fields=['document_id'], condition=Q(active=True), name='unique_active_docid'),
            UniqueConstraint(fields=['document_id', 'version_number'], name='version_by_document'),
        ]

    def __str__(self):
        return self.title_name

    def get_absolute_url(self):
        return reverse('main:document_detail',
                       kwargs={
                           'inst_slug': self.parent_ref_number.holding_institution.institution_slug,
                           'ref_slug': self.parent_ref_number.ref_number_slug,
                           'doc_slug': self.document_slug
                       })

    def get_absolute_version_url(self):
        return reverse('main:document_legacy_detail',
                       kwargs={
                           'inst_slug': self.parent_ref_number.holding_institution.institution_slug,
                           'ref_slug': self.parent_ref_number.ref_number_slug,
                           'doc_slug': self.document_slug,
                           'version_nr': self.version_number
                       })

    # model method to return queryset of all versions with the same document_id
    def get_versions(self):
        versions = type(self).all_objects.filter(document_id=self.document_id).order_by('-document_utc_add')
        return versions

    def save(self, force_update=False, *args, **kwargs):
        """Save the current instance.

        Custom behaviour: This will normally create a new object in storage every time, marking any previous
        versions (i.e. sharing the same document_id) as inactive.
        Note that this only applies to manual calls to save(), not other methods like update().

        To operate on the existing model instead (e.g. for quickfixes), set force_update=True. This only works for
        objects which have been saved before and will raise ValueError for pk=None, or DatabaseError for unknown pks.
        This option cannot be combined with force_insert.

        Subscriptions: if a change happens, subscriptions are checked and Notifications are created.
        """
        if not force_update:
            old_doc_id = self.pk

            # Save a new version alongside any old ones
            self.pk = None
            # Set all old versions to be inactive
            type(self).all_objects.filter(document_id=self.document_id).exclude(pk=self.pk).update(active=False)
            # increment version_number by 1
            try:
                self.get_versions().latest()
                self.version_number = self.get_versions().exclude(pk=self.pk).latest().version_number + 1
            except type(self).DoesNotExist:
                self.version_number = 1

            # Check Subscriptions:
            old_ref_id = self.parent_ref_number.id
            old_user_id = self.submitted_by.id

            # Gets all document subscriptions for the current document
            doc_subscriptions = UserSubscription.objects.filter(subscription_type=UserSubscription.SubscriptionType.DOCUMENT,
                                                                object_id=old_doc_id)
            for d_sub in doc_subscriptions:
                UserNotification.objects.create(subscription=d_sub, user=d_sub.user,
                                                subject=_(f'Document {self.title_name} changed'),
                                                message='A document changed. For realz!')

            # Gets all ref_number subscriptions for the current document
            ref_subscriptions = UserSubscription.objects.filter(subscription_type=UserSubscription.SubscriptionType.REF_NUMBER,
                                                                object_id=old_ref_id)
            for r_sub in ref_subscriptions:
                UserNotification.objects.create(subscription=r_sub, user=r_sub.user,
                                                subject='A ref changed',
                                                message='A ref changed. For realz!')

            usr_subscriptions = UserSubscription.objects.filter(subscription_type=UserSubscription.SubscriptionType.USER,
                                                                object_id=old_user_id)
            for u_sub in usr_subscriptions:
                UserNotification.objects.create(subscription=u_sub, user=u_sub.user,
                                                subject='A usr changed',
                                                message='A usr changed. For realz!')

        super().save(force_update=force_update, *args, **kwargs)


class UserManager(BaseUserManager):
    """Custom UserManager for transcriptiones."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('Please enter an e-mail address'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):

        # normalize passwords if created from form.cleaned_data
        if 'password1' in extra_fields and 'password2' in extra_fields:
            password = extra_fields.pop('password1')
            del extra_fields['password2']

        extra_fields.setdefault('email_confirmed', False)
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('All superusers must have is_staff = True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('All superusers must have is_superuser = True'))

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model for the transcriptiones project."""
    class NotificationPolicy(models.IntegerChoices):
        NONE = 1, _('No notification E-Mails')
        IMMEDIATE = 2, _('Every time a subscribed document has changed.')
        DAILY = 3, _('Once a day, only if changes happened.')
        WEEKLY = 4, _('Once a week, only if changes happened.')

    class MessageNotificationPolicy(models.IntegerChoices):
        NONE = 1, _('No notification E-Mails')
        IMMEDIATE = 2, _('Every time a message is sent.')
        DAILY = 3, _('Once a day, only if you received messages.')

    username = models.CharField(verbose_name=_('Username'),
                                unique=True,
                                max_length=150,
                                blank=False,
                                help_text=_('Provide a user name'))

    first_name = models.CharField(verbose_name=_('First name'),
                                  max_length=150,
                                  blank=False,
                                  help_text='Enter your first name(s)')

    last_name = models.CharField(verbose_name=_('Last name'),
                                 max_length=150,
                                 blank=False,
                                 help_text=_('Enter your last name'))

    email = models.EmailField(verbose_name=_('Email'),
                              unique=True,
                              max_length=255,
                              blank=False,
                              help_text=_('Enter your email address'))

    email_confirmed = models.BooleanField(_('Email confirmed'),
                                          default=True,     # TODO Why?
                                          help_text=_('Has the user confirmed the email address?'))

    is_staff = models.BooleanField(verbose_name=_('Staff status'),
                                   default=False,
                                   help_text=_('Does the user have staff status and can thus login to the admin page?'))

    is_active = models.BooleanField(verbose_name=_('Active'),
                                    default=True,
                                    help_text=_('Is the user active? Users get deactivated instead of deleted.'))

    date_joined = models.DateTimeField(verbose_name=_('Date joined'),
                                       auto_now_add=True)

    mark_anonymous = models.BooleanField(verbose_name=_('Mark anonymous by default'),
                                         default=False,
                                         help_text=_('If selected, your documents will be published anonymously by '
                                                     'default. Can be changed on a document basis.'))

    user_orcid = models.CharField(verbose_name=_('Orcid'), default='', max_length=255,
                                  help_text=_('User id from https://orcid.org/'))

    notification_policy = models.IntegerField(verbose_name=_('Subscription Notification policy'),
                                              choices=NotificationPolicy.choices,
                                              default=NotificationPolicy.DAILY,
                                              help_text=_('How often do you want to be notified about your subscribed '
                                                          'documents?'))

    message_notification_policy = models.IntegerField(verbose_name=_('Message Notification policy'),
                                                      choices=MessageNotificationPolicy.choices,
                                                      default=MessageNotificationPolicy.IMMEDIATE,
                                                      help_text=_('How often do you want to be notified about messages '
                                                                  'you receive?'))

    different_editor_subscription = models.BooleanField(verbose_name=_('Subscription to owned documents'),
                                                        help_text=_('Do you want to be notified when your '
                                                                    'documents were edited by another user?'),
                                                        default=True)

    ui_language = models.CharField(max_length=20,
                                   verbose_name=_('Default User Interface Language'),
                                   help_text=_('What is your preferred language?'),
                                   choices=settings.LANGUAGES,
                                   default='en')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def get_absolute_url(self):
        return reverse('main:public_profile', kwargs={'username': self.username})

    def get_user_state_badge(self):
        str_user = _('Benutzer')
        str_staff = _('Mitarbeiter')
        str_admin = _('Admin')

        ret_value = f'<span class="badge badge-info">{str_user}</span>'
        if self.is_staff:
            ret_value = f'<span class="badge badge-warning">{str_staff}</span>'
        if self.is_superuser:
            ret_value = f'<span class="badge badge-danger">{str_admin}</span>'

        return mark_safe(ret_value)

    def get_user_activity_badge(self):
        str_active = _('Active')
        str_inactive = _('Inactive')
        activity_state = f'<span class="badge badge-success">{str_active}</span>'
        if not self.is_active:
            activity_state = f'<span class="badge badge-secondary">{str_inactive}</span>'
        return mark_safe(activity_state)


class UserSubscription(models.Model):
    class SubscriptionType(models.IntegerChoices):
        REF_NUMBER = 1, _('Reference number')
        DOCUMENT = 2, _('Document')
        USER = 3, _('User')
        AUTHOR = 4, _('Author')
        INSTITUTION = 5, _('Institution')
        SOURCE_TYPE = 6, _('Source Type')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_type = models.IntegerField(choices=SubscriptionType.choices)
    object_id = models.BigIntegerField()


class UserMessage(models.Model):
    receiving_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tc_msg_rec_user')
    sending_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tc_msg_send_user')

    subject = models.CharField(max_length=250)
    message = models.TextField()

    # 0 = new, 1 = read
    viewing_state = models.IntegerField(default=0)
    sending_time = models.DateTimeField(auto_now_add=True)


class UserNotification(models.Model):
    subscription = models.ForeignKey(UserSubscription, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    subject = models.CharField(max_length=250)
    message = models.TextField()

    # 0 = new, 1 = read
    viewing_state = models.IntegerField(default=0)
    sending_time = models.DateTimeField(auto_now_add=True)


class ContactMessage(models.Model):
    reply_email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()

    # assignee = models.ForeignKey(User, on_delete=models.CASCADE)

    state = models.IntegerField(default=0)
    sending_time = models.DateTimeField(auto_now_add=True)

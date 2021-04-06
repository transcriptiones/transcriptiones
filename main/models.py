import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone

from partial_date import PartialDateField
from django_countries.fields import CountryField
from i18n_model.models import I18nModel


class Institution(models.Model):
    """An institution is a physical location which holds documents. These documents have a reference number.
    Reference numbers are always associated with an institution."""

    institution_name = models.CharField(verbose_name=_("institution"),
                                        max_length=80,
                                        unique=True,
                                        help_text=_("Complete name of the institution"))

    street = models.CharField(verbose_name=_("street"),
                              max_length=80,
                              help_text=_("Street"))

    zip_code = models.IntegerField(verbose_name=_("zip code"),
                                   help_text=_("Zip code"))

    city = models.CharField(verbose_name=_("city"),
                            max_length=100,
                            help_text=_("City"))

    country = CountryField(verbose_name=_("country"),
                           help_text=_("Country"))

    site_url = models.URLField(verbose_name=_("website"),
                               max_length=200,
                               blank=True,
                               help_text=_("URL of the Website"))

    institution_utc_add = models.DateTimeField(auto_now_add=True)
    institution_slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = _("institution")
        verbose_name_plural = _("institutions")

    def __str__(self):
        return self.institution_name

    def get_absolute_url(self):
        # TODO
        return reverse('institution_detail', kwargs={'instslug': self.institution_slug})


class RefNumber(models.Model):
    """Physical Collections are identified by a reference number (RefNumber). These collections can contain multiple
    documents with multiple pages."""

    holding_institution = models.ForeignKey(Institution,
                                            verbose_name=_("institution"),
                                            on_delete=models.PROTECT,
                                            related_name="ref_numbers",  # TODO
                                            help_text=_("Institution associated with this reference number"))

    ref_number_name = models.CharField(verbose_name=_("reference number"),
                                       max_length=100,
                                       help_text=_("reference number of the collection containing a document"))

    ref_number_title = models.CharField(verbose_name=_("title"),
                                        max_length=150,
                                        blank=True,
                                        help_text=_("Title of the collection"))

    collection_link = models.URLField(verbose_name=_("static URL"),
                                      max_length=200,
                                      blank=True,
                                      help_text=_("Link to the collection"))

    ref_number_utc_add = models.DateTimeField(auto_now_add=True)
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
        return reverse('ref_number_detail',     # TODO
                       kwargs={'instslug': self.holding_institution.institution_slug, 'refslug': self.refnumber_slug})


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

    class Meta:
        verbose_name = _("Document author")
        verbose_name_plural = _("Document authors")

    def __str__(self):
        return self.author_name


class SourceLanguage(models.Model):
    """Documents are written in certain languages. This table contains these languages with their ISO 639-3 Codes.
    TODO: Remove this model
    """
    language_name = models.CharField(verbose_name=_("Language"),
                                     max_length=50)

    language_code = models.CharField(verbose_name=_("ISO 639-3 code"),
                                     max_length=3)

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

    def __str__(self):
        return self.language_name


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
        verbose_name = "archivalienart"
        verbose_name_plural = "archivalienarten"

    def __str__(self):
        return self.type_name


class SourceTypeI18N(I18nModel):
    class Meta:
        source_model = SourceType
        translation_fields = ('type_name', )


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

    parent_institution = models.ForeignKey(Institution,
                                           verbose_name="institution",
                                           related_name="documents",
                                           on_delete=models.PROTECT,
                                           help_text="Institution, welche die Quelle aufbewahrt")

    parent_refnumber = models.ForeignKey(RefNumber,
                                         verbose_name="signatur",
                                         related_name="documents",
                                         on_delete=models.PROTECT,
                                         help_text="Signatur der Quelle")

    author = models.ManyToManyField(Author,
                                    verbose_name="beteiligte Personen",
                                    blank=True,
                                    help_text="Autor*innen, Kopist*innen, Editor*innen",
                                    related_name="works",)

    doc_start_date = PartialDateField(verbose_name=_("Creation period start"),)

    doc_end_date = PartialDateField(verbose_name=_("Creation period end"),
                                    blank=True)

    place_name = models.CharField(verbose_name="entstehungsort",
                                  max_length=150,
                                  blank=False,
                                  help_text="Entstehungsort der Quelle")

    language = models.ManyToManyField(SourceLanguage,
                                      verbose_name="sprachen",
                                      blank=True,
                                      help_text="In der Quelle verwendete Sprachen")

    source_type = models.ForeignKey(SourceType,
                                    verbose_name="archivalienart",
                                    on_delete=models.PROTECT,
                                    blank=False,
                                    null=False,
                                    help_text="Archivalienart/Quellengattung")

    material = models.CharField(verbose_name="beschreibstoff",
                                max_length=15,
                                blank=True,
                                choices=MaterialType.choices,
                                help_text="Beschreibstoff")

    measurements_length = models.DecimalField(verbose_name="länge",
                                              max_digits=5,
                                              decimal_places=1,
                                              blank=True,
                                              null=True,
                                              help_text="Länge in cm")

    measurements_width = models.DecimalField(verbose_name="breite",
                                             max_digits=5,
                                             decimal_places=1,
                                             blank=True,
                                             null=True,
                                             help_text="Breite in cm")

    pages = models.PositiveSmallIntegerField(verbose_name="anzahl Seiten",
                                             blank=True,
                                             null=True,
                                             help_text="Umfang der Quelle")

    paging_system = models.CharField(verbose_name="paginierung",
                                     max_length=15,
                                     blank=True,
                                     choices=PaginationType.choices,
                                     help_text="Paginierungssystem")

    illuminated = models.BooleanField(null=True,
                                      verbose_name="illuminiert",
                                      help_text="Ist die Quelle illuminiert?")

    transcription_scope = models.TextField(verbose_name="transkribierte Teile des Dokuments",
                                           help_text="Liste der transkribierten Abschnitte/Seiten/Kapitel")

    comments = models.TextField(blank=True,
                                verbose_name="editorische und inhaltliche Anmerkungen",
                                help_text="Platz für editorische und inhaltliche Anmerkungen")

    transcription_text = models.TextField(verbose_name="transkription",
                                          help_text="Transkription")

    document_utc_add = models.DateTimeField(verbose_name=_("upload date"),
                                            auto_now_add=True)

    # TODO i dont get it
    User = settings.AUTH_USER_MODEL

    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     verbose_name="eingereicht durch",
                                     on_delete=models.PROTECT,  # Users are not supposed to be delible
                                     related_name="contributions",
                                     help_text="Benutzer*in, die/der diese Transkription eingereicht hat",
                                     editable=False)

    submitted_by_anonymous = models.BooleanField(verbose_name=_("Anonymous"),
                                                 default=False,
                                                 help_text=_("Select this, if you want to publish this "
                                                             "document anonymously"))

    document_slug = models.SlugField()

    active = models.BooleanField(default=True, editable=False)  # Whether this is the latest version

    commit_message = models.CharField(verbose_name=_("Changes"),
                                      max_length=255,
                                      default="initial",
                                      help_text=_("A brief description of the applied changes."))

    version_number = models.IntegerField(verbose_name=_("version number"),
                                         default=1,
                                         help_text=_("Version number"))

    # TODO I don't get it
    objects = DocumentManager()  # Only current versions
    all_objects = models.Manager()  # Absolutely all objects, even outdated versions

    class Meta:
        verbose_name = "dokument"
        verbose_name_plural = "dokumente"
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
        return reverse('documenttitledetail',
                       kwargs={
                           'instslug': self.parent_institution.institution_slug,
                           'refslug': self.parent_refnumber.refnumber_slug,
                           'docslug': self.document_slug
                       })

    def get_absolute_version_url(self):
        return reverse('documenttitlelegacydetail',
                       kwargs={
                           'instslug': self.parent_institution.institution_slug,
                           'refslug': self.parent_refnumber.refnumber_slug,
                           'docslug': self.document_slug,
                           'versionnr': self.version_number
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
        """
        if not force_update:
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
        super().save(force_update=force_update, *args, **kwargs)


class DocumentPage(models.Model):
    """A document is made up of pages. Ideally these pages correspond to physical pages but at the end a
     DocumentPage is a part of a Document."""

    seal = models.BooleanField(verbose_name=_("Seal"),
                               null=True,
                               help_text=_("Are there any seals on this page?"))


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

    username = models.CharField(verbose_name=_('username'),
                                unique=True,
                                max_length=150,
                                blank=False,
                                help_text=_('Provide a user name'))

    first_name = models.CharField(verbose_name=_('first name'),
                                  max_length=150,
                                  blank=False,
                                  help_text='Enter your first name(s)')

    last_name = models.CharField(verbose_name=_('last name'),
                                 max_length=150,
                                 blank=False,
                                 help_text=_('Enter your last name'))

    email = models.EmailField(verbose_name=_('email'),
                              unique=True,
                              max_length=255,
                              blank=False,
                              help_text=_('Enter your email address'))

    email_confirmed = models.BooleanField(_('email confirmed'),
                                          default=True,     # TODO Why?
                                          help_text=_('Has the user confirmed the email address?'))

    is_staff = models.BooleanField(verbose_name=_('staff status'),
                                   default=False,
                                   help_text=_('Does the user have staff status and can thus login to the admin page?'))

    is_active = models.BooleanField(verbose_name=_('active'),
                                    default=True,
                                    help_text=_('Is the user active? Users get deactivated instead of deleted.'))

    date_joined = models.DateTimeField(verbose_name=_('date joined'),
                                       auto_now_add=True)

    mark_anonymous = models.BooleanField(verbose_name=_('Mark anonymous by default'),
                                         default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']
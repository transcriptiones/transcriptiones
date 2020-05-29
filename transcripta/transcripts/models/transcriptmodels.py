import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q, Max, UniqueConstraint
from django.urls import reverse


class Institution(models.Model):
    institution_name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name="institution",
        help_text="Vollständiger Name der Institution"
        )
    street = models.CharField(
        max_length=50,
        verbose_name="strasse",
        help_text="Strasse"
        )
    zip_code = models.PositiveSmallIntegerField(
        verbose_name="postleitzahl",
        help_text="PLZ"
        )
    city = models.CharField(
        max_length=30,
        verbose_name="ort",
        help_text="Ort"
        )
    country = models.CharField(
        max_length=50,
        verbose_name="land",
        help_text="Land"
        )
    site_url = models.URLField(
        max_length=200,
        blank=True,
        verbose_name="website",
        help_text="URL der Website"
        )
    institution_utc_add = models.DateTimeField(
        auto_now_add=True)
    institution_slug = models.SlugField(
        unique=True,
        )

    class Meta:
        verbose_name = "institution"
        verbose_name_plural = "institutionen"
    
    def __str__(self):
        return self.institution_name

    def get_absolute_url(self):
        return reverse('institutiondetail', kwargs={'instslug': self.institution_slug})


class RefNumber(models.Model):
    holding_institution = models.ForeignKey(
        Institution,
        on_delete=models.PROTECT,
        related_name="refnumbers",
        verbose_name="institution",
        help_text="Institution, welche die Signatur beherbergt"
        )
    refnumber_name = models.CharField(
        max_length=100,
        verbose_name="signatur",
        help_text="Signatur der Verzeichniseinheit"
        )
    refnumber_title = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="titel",
        help_text="Titel der Verzeichniseinheit"
        )
    collection_link = models.URLField(
        max_length=200,
        blank=True,
        verbose_name="link zum Archivbestand",
        help_text="Link zum Archivbestand"
        )
    refnumber_utc_add = models.DateTimeField(
        auto_now_add=True)
    refnumber_slug = models.SlugField(
        unique=True,
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['refnumber_name', 'holding_institution'], name='unique_refnumber'),
            ]

        verbose_name = "signatur"
        verbose_name_plural = "signaturen"

    def __str__(self):
        return self.refnumber_name

    def get_absolute_url(self):
        return reverse('refnumberdetail', kwargs={'instslug': self.holding_institution.institution_slug, 'refslug': self.refnumber_slug})

class Author(models.Model):
    author_name = models.CharField(max_length=150, verbose_name="name der beteiligten Person")

    class Meta:
        verbose_name = "beteiligte Person"
        verbose_name_plural = "beteiligte Personen"

    def __str__(self):
        return self.author_name

class SourceLanguage(models.Model):
    language_name = models.CharField(max_length=50, verbose_name="sprache")
    language_code = models.CharField(max_length=3, verbose_name="ISO 639-3 Code")

    class Meta:
        verbose_name = "sprache"
        verbose_name_plural = "sprachen"

    def __str__(self):
        return self.language_name

class SourceType(models.Model):
    type_name = models.CharField(max_length=50, verbose_name="archivalienart")
    parent_type = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name="child_type", verbose_name="übergeordnete Archivalienart")

    class Meta:
        verbose_name = "archivalienart"
        verbose_name_plural = "archivalienarten"

    def __str__(self):
        return self.type_name


class DocumentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)

    def search(self, kwargs):
        qs = self.get_queryset()
        
        if kwargs.get('b1') == 'is':
            if kwargs.get('f1') == 'institution':
                qs = qs.filter(parent_institution__institution_name=kwargs.get('q1'))

            if kwargs.get('f1') == 'refnumber':
                qs = qs.filter(parent_refnumber__refnumber_name=kwargs.get('q1'))

        if kwargs.get('b1') == 'isnot':
            if kwargs.get('f1') == 'institution':
                qs = qs.exclude(parent_institution__institution_name=kwargs.get('q1'))

            if kwargs.get('f1') == 'refnumber':
                qs = qs.exclude(parent_refnumber__refnumber_name=kwargs.get('q1'))
        
        if kwargs.get('b1') == 'contains':
            if kwargs.get('f1') == 'institution':
                qs = qs.filter(parent_institution__institution_name__icontains=kwargs.get('q1'))

            if kwargs.get('f1') == 'refnumber':
                qs = qs.filter(parent_refnumber__refnumber_name__icontains=kwargs.get('q1'))

        return qs


class DocumentTitle(models.Model):

    YesNoChoices = models.TextChoices('YesNo', 'JA NEIN')
    MatChoices = models.TextChoices('MaterialType', 'PAPIER PERGAMENT PAPYRUS')
    PagChoices = models.TextChoices('PaginationType', 'PAGINIERUNG FOLIIERUNG')
    MonthChoices = models.IntegerChoices('Month', 'JANUAR FEBRUAR MÄRZ APRIL MAI JUNI '
                                                  'JULI AUGUST SEPTEMBER OKTOBER NOVEMBER DEZEMBER')
    DayChoices = models.IntegerChoices('Day', [str(n) for n in range(1, 32)])

    document_id = models.UUIDField(
        default=uuid.uuid1,
        editable=False,
        verbose_name="urtext-id",
        help_text="ID des Urtexts; konstant zwischen aktuellen und alten Versionen einer Transkription",
    )
    title_name = models.CharField(
        max_length=200,
        verbose_name="titel",
        help_text="Titel des Dokuments"
        )
    parent_institution = models.ForeignKey(
        Institution,
        related_name="documents",
        on_delete=models.PROTECT,
        verbose_name="institution",
        help_text="Institution, welche die Quelle aufbewahrt"
        )
    parent_refnumber = models.ForeignKey(
        RefNumber,
        related_name="documents",
        on_delete=models.PROTECT,
        verbose_name="signatur",
        help_text="Signatur der Quelle"
        )
    author = models.ManyToManyField(
        Author,
        blank=True,
        verbose_name="beteiligte Personen",
        help_text="Autor*innen, Kopist*innen, Editor*innen"
        )
    start_year = models.SmallIntegerField(
        blank=True,
        null=True,
        verbose_name="startjahr",
        help_text="YYYY"
        )
    start_month = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="startmonat",
        help_text="MM",
        choices=MonthChoices.choices
        ) 
    start_day = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="starttag",
        help_text="DD",
        choices=DayChoices.choices
        )
    end_year = models.SmallIntegerField(
        blank=True,
        null=True,
        verbose_name="endjahr",
        help_text="YYYY"
        )
    end_month = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="endmonat",
        help_text="MM",
        choices=MonthChoices.choices
        )
    end_day = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="endtag",
        help_text="DD",
        choices=DayChoices.choices
        )
    place_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="entstehungsort",
        help_text="Entstehungsort der Quelle"
        )
    language = models.ManyToManyField(
        SourceLanguage,
        blank=True,
        verbose_name="sprachen",
        help_text="In der Quelle verwendete Sprachen"
        )
    source_type = models.ForeignKey(
        SourceType,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="archivalienart",
        help_text="Archivalienart/Quellengattung"
        )
    material = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="beschreibstoff",
        choices=MatChoices.choices,
        help_text="Beschreibstoff"
        )
    measurements_length = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        blank=True,
        null=True,
        verbose_name="länge",
        help_text="Länge in cm"
        )
    measurements_width = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        blank=True,
        null=True,
        verbose_name="breite",
        help_text="Breite in cm"
        )
    pages = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="anzahl Seiten",
        help_text="Umfang der Quelle"
        )
    paging_system = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="paginierungssystem",
        choices=PagChoices.choices,
        help_text="Paginierungssystem"
        )
    illuminated = models.CharField(
        max_length=4,
        blank=True,
        verbose_name="illuminiert",
        choices=YesNoChoices.choices,
        help_text="Ist die Quelle illuminiert?"
        )
    seal = models.CharField(
        max_length=4,
        blank=True,
        verbose_name="siegel",
        choices=YesNoChoices.choices,
        help_text="Sind Siegel erhalten?"
        )
    transcription_scope = models.TextField(
        verbose_name="transkribierte Teile des Dokuments",
        help_text="Liste der transkribierten Abschnitte/Seiten/Kapitel"
        )
    comments = models.TextField(
        blank=True,
        verbose_name="editorische und inhaltliche Anmerkungen",
        help_text="Platz für editorische und inhaltliche Anmerkungen"
        )
    transcription_text = models.TextField(
        verbose_name="transkription",
        help_text="Transkription"
        )
    document_utc_add = models.DateTimeField(
        auto_now_add=True,
        verbose_name="einreichungsdatum",
    )
    User = settings.AUTH_USER_MODEL
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,  # Users are not supposed to be delible
        related_name="contributions",
        verbose_name="eingereicht durch",
        help_text="Benutzer*in, die/der diese Transkription eingereicht hat",
        editable=False
    )
    submitted_by_anonymous = models.BooleanField(
        default=False,
        verbose_name="Anonymer Beitrag",
        help_text="Anwählen, um bei der Transkription keinen Benutzernamen anzuzeigen",
    )
    document_slug = models.SlugField()
    active = models.BooleanField(default=True, editable=False)  # Whether this is the latest version
    commit_message = models.CharField(
        max_length=255,
        verbose_name="Änderungen",
        help_text="Knappe Beschreibung der Änderungen",
        default="initial"
        )

    objects = DocumentManager()  # Only current versions
    all_objects = models.Manager()  # Absolutely all objects, even outdated versions

    class Meta:
        verbose_name = "dokument"
        verbose_name_plural = "dokumente"
        get_latest_by = "document_utc_add"
        constraints = [
            UniqueConstraint(fields=['document_slug'], condition=Q(active=True), name='unique_active_slug'),
            UniqueConstraint(fields=['document_id'], condition=Q(active=True), name='unique_active_docid'),
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

    #model method to return queryset of all versions with the same document_id
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
        super().save(force_update=force_update, *args, **kwargs)

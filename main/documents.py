from datetime import date, timedelta
from typing import Optional

from django.db.models import QuerySet
from django_elasticsearch_dsl import Document as ElasticsearchDocument, fields, DEDField, DateField
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Range, DateRange, IntegerRange
from partial_date import PartialDate
from rest_framework.fields import DateTimeField

from main.analyzers import transcript_analyzer, transcript_analyzer2, default_analyzer
from main.models import Document, Author, RefNumber, Language, Institution


@registry.register_document
class TranscriptionDocument(ElasticsearchDocument):
    """Elasticsearch index mapping for DocumentTitle models.
    Intended for user search, not storage or internal search.
    """
    title_name = fields.TextField(fields={"keyword": fields.KeywordField()}, analyzer=default_analyzer)
    # title_name = fields.TextField()
    doc_start_date = DateField()
    doc_end_date = DateField()
    transcription_text = fields.TextField(analyzer=transcript_analyzer)
    # author = fields.TextField(multi=True, fields={"keyword": fields.KeywordField()})

    institution_name = fields.TextField(attr="parent_ref_number.holding_institution.institution_name",
                                        fields={"keyword": fields.KeywordField()},
                                        analyzer=default_analyzer)

    ref_number_title = fields.TextField(attr="parent_ref_number.ref_number_title", analyzer=default_analyzer)
    ref_number_name = fields.TextField(attr="parent_ref_number.ref_number_name")
    # language = fields.KeywordField(multi=True)
    source_type = fields.KeywordField(attr="source_type.type_name")
    material = fields.KeywordField()
    paging_system = fields.KeywordField()
    place_name = fields.TextField(fields={"keyword": fields.KeywordField()}, analyzer=default_analyzer)

    class Django:
        model = Document
        fields = [
            'pages',
            'illuminated',
            'seal',
        ]
        related_models = [Author, RefNumber, Language]

    class Index:
        name = 'transcriptiones_idx'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    def prepare_doc_start_date(self, instance: PartialDate):
        return instance.doc_start_date.date.year

    def prepare_doc_end_date(self, instance: PartialDate):
        if instance.doc_end_date is not None:
            if isinstance(instance.doc_end_date, str):
                return instance.doc_start_date.date.year
            elif isinstance(instance.doc_end_date, PartialDate):
                return instance.doc_end_date.date.year

        return instance.doc_start_date.date.year


    @staticmethod
    def prepare_author(instance: Document) -> list:
        """Compose a document's author field."""
        return [author.author_name for author in instance.author.all()]

    @staticmethod
    def prepare_language(instance: Document) -> list:
        """Compose a document's language field."""
        return [language.name for language in instance.language.all()]

    @classmethod
    def prepare_year(cls, instance: Document) -> Optional[Range]:
        """Compose a document's date range field.

        Will write None if there is no information whatsoever. This is because Range() would cause the entry to be
        found no matter the filter.
        """
        """
        if instance.start_year is None:
            return None
        return Range(gte=instance.start_year, lte=instance.end_year or instance.start_year)
        """
        return None

    @classmethod
    def prepare_date(cls, instance: Document) -> Optional[Range]:
        """Compose a document's date range field.

        Will write None if there is no information whatsoever. This is because Range() would cause the entry to be
        found no matter the filter.
        """
        """
        if instance.start_year is None:
            return None
        min_date = date(instance.start_year, instance.start_month or 1, instance.start_day or 1)
        max_month = instance.end_month or instance.start_month or 12
        max_day = instance.end_day or instance.start_day or cls._last_day_in_month(max_month)
        max_date = date(instance.end_year or instance.start_year, max_month, max_day)
        return Range(gte=min_date, lte=max_date)
        """
        return None

    @staticmethod
    def _last_day_in_month(month: int) -> int:
        """Gives the number of days in a given month."""
        return (date(420, month % 12 + 1, 1) - timedelta(days=1)).day

    def get_queryset(self):
        queryset: QuerySet = super().get_queryset()
        #return queryset.filter(active=True).select_related('parent_ref_number').prefetch_related('author', 'language')
        return queryset

    @staticmethod
    def get_instances_from_related(related_instance):
        if isinstance(related_instance, Institution):
            docs = list()
            for ref_set in related_instance.refnumber_set.all():
                docs += ref_set.document_set.all()
            return docs
        if isinstance(related_instance, Author):
            return related_instance.document_set.all()
        if isinstance(related_instance, RefNumber):
            return related_instance.document_set.all()
        if isinstance(related_instance, Language):
            return related_instance.document_set.all()
        raise TypeError


@registry.register_document
class TranscriptionDocumentStrict(ElasticsearchDocument):
    """Elasticsearch index mapping for DocumentTitle models.
    Intended for user search, not storage or internal search.
    """
    title_name = fields.TextField(fields={"keyword": fields.KeywordField()})
    # title_name = fields.TextField()
    doc_start_date = DateField()
    doc_end_date = DateField()
    transcription_text = fields.TextField(analyzer=transcript_analyzer2)
    # author = fields.TextField(multi=True, fields={"keyword": fields.KeywordField()})

    institution_name = fields.TextField(attr="parent_ref_number.holding_institution.institution_name",
                                        fields={"keyword": fields.KeywordField()})

    ref_number_title = fields.TextField(attr="parent_ref_number.ref_number_title")
    ref_number_name = fields.TextField(attr="parent_ref_number.ref_number_name")
    # language = fields.KeywordField(multi=True)
    source_type = fields.KeywordField(attr="source_type.type_name")
    material = fields.KeywordField()
    paging_system = fields.KeywordField()
    place_name = fields.TextField(fields={"keyword": fields.KeywordField()})

    class Django:
        model = Document
        fields = [
            'pages',
            'illuminated',
            'seal',
        ]
        related_models = [Author, RefNumber, Language]

    class Index:
        name = 'transcriptiones_idx_strict'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    def prepare_doc_start_date(self, instance: PartialDate):
        return instance.doc_start_date.date.year

    def prepare_doc_end_date(self, instance: PartialDate):
        if instance.doc_end_date is not None:
            if isinstance(instance.doc_end_date, str):
                return instance.doc_start_date.date.year
            elif isinstance(instance.doc_end_date, PartialDate):
                return instance.doc_end_date.date.year

        return instance.doc_start_date.date.year


    @staticmethod
    def prepare_author(instance: Document) -> list:
        """Compose a document's author field."""
        return [author.author_name for author in instance.author.all()]

    @staticmethod
    def prepare_language(instance: Document) -> list:
        """Compose a document's language field."""
        return [language.name for language in instance.language.all()]

    @classmethod
    def prepare_year(cls, instance: Document) -> Optional[Range]:
        """Compose a document's date range field.

        Will write None if there is no information whatsoever. This is because Range() would cause the entry to be
        found no matter the filter.
        """
        """
        if instance.start_year is None:
            return None
        return Range(gte=instance.start_year, lte=instance.end_year or instance.start_year)
        """
        return None

    @classmethod
    def prepare_date(cls, instance: Document) -> Optional[Range]:
        """Compose a document's date range field.

        Will write None if there is no information whatsoever. This is because Range() would cause the entry to be
        found no matter the filter.
        """
        """
        if instance.start_year is None:
            return None
        min_date = date(instance.start_year, instance.start_month or 1, instance.start_day or 1)
        max_month = instance.end_month or instance.start_month or 12
        max_day = instance.end_day or instance.start_day or cls._last_day_in_month(max_month)
        max_date = date(instance.end_year or instance.start_year, max_month, max_day)
        return Range(gte=min_date, lte=max_date)
        """
        return None

    @staticmethod
    def _last_day_in_month(month: int) -> int:
        """Gives the number of days in a given month."""
        return (date(420, month % 12 + 1, 1) - timedelta(days=1)).day

    def get_queryset(self):
        queryset: QuerySet = super().get_queryset()
        #return queryset.filter(active=True).select_related('parent_ref_number').prefetch_related('author', 'language')
        return queryset

    @staticmethod
    def get_instances_from_related(related_instance):
        if isinstance(related_instance, Institution):
            docs = list()
            for ref_set in related_instance.refnumber_set.all():
                docs += ref_set.document_set.all()
            return docs
        if isinstance(related_instance, Author):
            return related_instance.document_set.all()
        if isinstance(related_instance, RefNumber):
            return related_instance.document_set.all()
        if isinstance(related_instance, Language):
            return related_instance.document_set.all()
        raise TypeError

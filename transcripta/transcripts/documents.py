from django.db.models import QuerySet
from django_elasticsearch_dsl import Document as ElasticsearchDocument, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer, token_filter, char_filter

from .models import DocumentTitle, Author, RefNumber, SourceLanguage

transcript_analyzer = analyzer(
    'transcript_analyzer',
    tokenizer="standard",
    filter=[
        "lowercase",
        token_filter('german_stop', 'stop', stopwords='_german_'),
        token_filter('german_snowball', 'snowball', language='German2'),
    ],
    char_filter=[
        "html_strip",
        char_filter('bracket_strip', 'mapping', mappings=['[ => ', '] => ']),
    ]
)


@registry.register_document
class TranscriptionDocument(ElasticsearchDocument):
    """Elasticsearch index mapping for DocumentTitle models.

    Intended for user search, not storage or internal search.
    """
    transcription_text = fields.TextField(analyzer=transcript_analyzer)
    author = fields.TextField(multi=True, fields={"keyword": fields.KeywordField()})
    title_name = fields.TextField(fields={"keyword": fields.KeywordField()})
    institution_name = fields.TextField(attr="parent_institution.institution_name", fields={"keyword": fields.KeywordField()})
    refnumber_title = fields.TextField(attr="parent_refnumber.refnumber_title")
    language = fields.KeywordField(multi=True)

    class Django:
        model = DocumentTitle
        fields = [
            'place_name',
            'measurements_length',
            'measurements_width',
            'pages',
            'illuminated',
            'seal',
            # ...
        ]
        related_models = [Author, RefNumber, SourceLanguage]

    class Index:
        name = 'transcripts'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    @staticmethod
    def prepare_author(instance: DocumentTitle) -> list:
        """Compose a document's author field"""
        return [author.author_name for author in instance.author.all()]

    @staticmethod
    def prepare_language(instance: DocumentTitle) -> list:
        """Compose a document's language field"""
        return [language.language_name for language in instance.language.all()]

    def get_queryset(self):
        queryset: QuerySet = super().get_queryset()
        return queryset.filter(active=True).select_related('parent_refnumber').prefetch_related('author', 'language')

    @staticmethod
    def get_instances_from_related(related_instance):
        if isinstance(related_instance, Author):
            return related_instance.works.all()
        if isinstance(related_instance, RefNumber):
            return related_instance.documents.all()
        raise TypeError

from django.db.models import QuerySet
from django_elasticsearch_dsl import Document as ElasticsearchDocument, fields
from django_elasticsearch_dsl.registries import registry

from .models import DocumentTitle, Author, RefNumber


@registry.register_document
class TranscriptionDocument(ElasticsearchDocument):
    """Elasticsearch index mapping for DocumentTitle models.

    Intended for user search, not storage or internal search.
    """
    author = fields.TextField(multi=True, fields={"keyword": fields.KeywordField()})
    refnumber_title = fields.TextField(attr="parent_refnumber.refnumber_title")
    language = fields.KeywordField(multi=True)

    class Django:
        model = DocumentTitle
        fields = [
            'title_name',
            'transcription_text',
            'place_name',
            'measurements_length',
            'measurements_width',
            'pages',
            'illuminated',
            'seal',
            # ...
        ]
        related_models = [Author, RefNumber]

    class Index:
        name = 'transcripts'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    @staticmethod
    def prepare_author(instance: DocumentTitle) -> list:
        return [author.author_name for author in instance.author.all()]

    @staticmethod
    def prepare_language(instance: DocumentTitle) -> list:
        return [language.language_name for language in instance.language.all()]

    def get_queryset(self):
        queryset: QuerySet = super().get_queryset()
        return queryset.select_related('parent_refnumber').prefetch_related('author')

    @staticmethod
    def get_instances_from_related(related_instance):
        if isinstance(related_instance, Author):
            return related_instance.works.all()
        if isinstance(related_instance, RefNumber):
            return related_instance.documents.all()
        raise TypeError

from datetime import datetime, timedelta

from django.test import TestCase, RequestFactory

from .models import Institution, User, DocumentTitle
from .views.uploadviews import AddDocumentView


class AddDocumentFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.institution = Institution.objects.create(
            institution_name='Testinstitut',
            street='Teststr. 123',
            zip_code=1234,
            city='Testhausen',
            country='Testland',
            site_url=''
        )
        cls.refnumber = cls.institution.refnumbers.create(
            refnumber_name='TEST 123456',
            refnumber_title='TEST',
            collection_link='',
            refnumber_slug='test123456'
        )
        cls.user = User.objects.create_user(
            username='testuser', email='test@test.ch', password='pwd')

    def setUp(self):
        self.factory = RequestFactory()
        self.testdocument_data = {
            'title_name': 'testtitle',
            'transcription_text': 'lol',
            'parent_institution': f'{self.institution.id}',
            'parent_refnumber': f'{self.refnumber.id}',
            'transcription_scope': 'komplett',
            'document_slug': 'testslug',
        }

    def test_object_creation(self):
        request = self.factory.post('/upload/', data=self.testdocument_data)
        request.user = self.user

        AddDocumentView.as_view()(request)
        self.assertEqual(DocumentTitle.objects.latest().title_name, 'testtitle')

    def test_submitted_by(self):
        request = self.factory.post('/upload/', data=self.testdocument_data)
        request.user = self.user

        AddDocumentView.as_view()(request)
        self.assertEqual(DocumentTitle.objects.latest().submitted_by, self.user)

    def test_creation_date(self):
        request = self.factory.post('/upload/', data=self.testdocument_data)
        request.user = self.user

        AddDocumentView.as_view()(request)
        edit_time = DocumentTitle.objects.latest().document_utc_add
        now = datetime.now(tz=edit_time.tzinfo)
        self.assertLessEqual(abs(now-edit_time), timedelta(seconds=1),
                             f"Creation time {edit_time} is too far from now ({now} {now.tzinfo}).")

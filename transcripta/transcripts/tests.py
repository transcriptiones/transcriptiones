import uuid
from datetime import datetime, timedelta

from django.db.utils import DatabaseError
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
        self.assertLessEqual(abs(now - edit_time), timedelta(seconds=1),
                             f"Creation time {edit_time} is too far from now ({now} {now.tzinfo}).")


class DocumentVersioningTest(TestCase):
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
        self.doc = DocumentTitle.all_objects.create(title_name='testtitle', transcription_text='lol',
                                                    parent_institution=self.institution,
                                                    parent_refnumber=self.refnumber, transcription_scope='komplett',
                                                    document_slug='testslug', submitted_by=self.user)
        self.pk1 = self.doc.pk
        self.doc.title_name = "Test Title (proper casing!)"
        self.doc.save()
        self.pk2 = self.doc.pk

    def test_separate_new_object(self):
        self.assertEqual(DocumentTitle.all_objects.filter(document_id=self.doc.document_id).count(), 2)
        self.assertNotEqual(self.pk1, self.pk2)
        self.assertNotEqual(DocumentTitle.all_objects.get(pk=self.pk1).title_name,
                            DocumentTitle.all_objects.get(pk=self.pk2).title_name)
        self.assertEqual(DocumentTitle.all_objects.get(pk=self.pk1).submitted_by,
                         DocumentTitle.all_objects.get(pk=self.pk2).submitted_by)

    def test_activity(self):
        self.assertFalse(DocumentTitle.all_objects.get(pk=self.pk1).active)
        self.assertTrue(DocumentTitle.all_objects.get(pk=self.pk2).active)

    def test_object_manager(self):
        query_set = DocumentTitle.objects.filter(document_id=self.doc.document_id)
        self.assertEqual(query_set.count(), 1)
        self.assertTrue(query_set.get().active)

    def test_force_update(self):
        newtitle = "New and improved testtitle!"
        initial_rowcount = DocumentTitle.all_objects.count()
        self.doc.title_name = newtitle
        self.doc.save(force_update=True)
        self.assertEqual(DocumentTitle.all_objects.get(pk=self.pk2).title_name, newtitle)
        self.assertEqual(DocumentTitle.all_objects.count(), initial_rowcount)

        # New, different object
        self.doc.pk = None
        self.doc.document_id = uuid.uuid1()
        with self.assertRaises(ValueError):
            self.doc.save(force_update=True)
        self.assertTrue(self.doc.active)

        self.doc.pk = 12345
        self.doc.document_id = uuid.uuid1()
        with self.assertRaises(DatabaseError):
            self.doc.save(force_update=True)
        self.assertTrue(self.doc.active)

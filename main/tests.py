from django.test import TestCase

from main.models import Document, RefNumber, Institution, User, SourceType, UserSubscription, UserNotification


class AnimalTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='soma',
                                   first_name='Sorin',
                                   last_name='Marti',
                                   email='soma@you.de',
                                   is_staff=False,
                                   is_active=True)

        user2 = User.objects.create(username='test',
                                    first_name='Sorin',
                                    last_name='Marti',
                                    email='soma2@you.de',
                                    is_staff=False,
                                    is_active=True)

        p_source_type = SourceType.objects.create(type_name='Parent',
                                                  parent_type=None)

        c_source_type = SourceType.objects.create(type_name='Child',
                                                  parent_type=p_source_type)

        institution = Institution.objects.create(institution_name='Sorins Home',
                                                 street='Dachsfelderstrasse 35',
                                                 zip_code='4053',
                                                 city='Basel',
                                                 country='ch',
                                                 site_url='https://whatever.ch',
                                                 institution_slug='sorins-home')

        ref_number = RefNumber.objects.create(holding_institution=institution,
                                              ref_number_name='#1234',
                                              ref_number_title='Ref Title',
                                              collection_link='https://whatever.ch',
                                              ref_number_slug='1234')

        doc = Document.objects.create(parent_ref_number=ref_number,
                                      title_name='Document title',
                                      doc_start_date='1907',
                                      transcription_text='<p>ABC</p>',
                                      submitted_by=user,
                                      source_type=c_source_type)

        sub_1 = UserSubscription.objects.create(user=user2,
                                                subscription_type=UserSubscription.SubscriptionType.USER,
                                                object_id=user.id)

        sub_2 = UserSubscription.objects.create(user=user2,
                                                subscription_type=UserSubscription.SubscriptionType.DOCUMENT,
                                                object_id=doc.id)

        sub_3 = UserSubscription.objects.create(user=user2,
                                                subscription_type=UserSubscription.SubscriptionType.REF_NUMBER,
                                                object_id=ref_number.id)

        self.test_doc_id = doc.id

    def test_doc_save(self):
        self.assertEqual(Document.objects.all().count(), 1)
        doc = Document.objects.get(id=self.test_doc_id)
        doc.transcription_text = '<p>DEF</p>'
        doc.save()
        self.assertEqual(Document.objects.all().count(), 1)
        self.assertEqual(Document.all_objects.all().count(), 2)
        self.assertEqual(Document.all_objects.filter(document_id=doc.document_id).count(), 2)

        self.assertEqual(UserNotification.objects.all().count(), 3)

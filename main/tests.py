from django.test import TestCase
from django.test import Client

from cron import send_weekly_notification_email
from main.models import Document, RefNumber, Institution, User, SourceType, UserSubscription, UserNotification, \
    UserManager


class MailTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='soma',
                                   first_name='Sorin',
                                   last_name='Marti',
                                   email='soma@you.de',
                                   is_staff=False,
                                   is_active=True)
        user.set_password('12345')
        user.notification_policy = User.NotificationPolicy.WEEKLY
        user.save()

    def test_weekly(self):
        send_weekly_notification_email()


class SourcetypeTestCase(TestCase):
    def test_sourcetype(self):
        st1 = SourceType.objects.create(type_name='test', parent_type=None)
        SourceType.objects.create(type_name='test_child1', parent_type=st1)
        SourceType.objects.create(type_name='test_child2', parent_type=st1)

        parent = SourceType.objects.get(id=st1.id)
        self.assertEqual(parent.child_type.count(), 2)


class UserTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='soma',
                                   first_name='Sorin',
                                   last_name='Marti',
                                   email='soma@you.de',
                                   is_staff=False,
                                   is_active=True)
        user.set_password('12345')
        user.save()



    def test_login(self):
        c = Client()
        logged_in = c.login(username='soma', password='12345')
        self.assertEqual(logged_in, True)

        manager = UserManager()
        user = manager.create_user("test@email.de")
        print(user)


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

    def test_i18n(self):
        pass



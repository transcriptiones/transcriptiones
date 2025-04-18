import datetime

from django.test import TestCase
from django.test import Client
from django.utils import timezone

from main.cron import send_weekly_notification_email
from main.cleanup import cleanup_users, cleanup_inst, cleanup_ref, cleanup_author
from main.models import Document, RefNumber, Institution, User, SourceType, UserSubscription, UserNotification, UserManager, Author


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



class CleanupTestCase(TestCase):
    def setUp(self):
        user_stay = User.objects.create(username='stay',
                                        first_name='Stacy',
                                        last_name='Rest',
                                        email='stay@here.com',
                                        is_staff=False)
        user_stay.set_password('12345')
        user_stay.save()

        user_go = User.objects.create(username='go',
                                      first_name='Goran',
                                      last_name='Flee',
                                      email='go@away.com',
                                      is_staff=False,
                                      email_confirmed=False,
                                      is_active=False,
                                      date_joined=timezone.now() - datetime.timedelta(hours=50))
        user_go.set_password('12345')
        user_go.save()

        inst_stay = Institution.objects.create(institution_name='Stayarchive',
                                   street='somestreet',
                                   zip_code='1234',
                                   city='somecity',
                                   country='ch',
                                   site_url='https://stayarchive.ch',
                                   institution_slug='stayarchive',
                                   created_by_id=user_stay.pk)

        inst_go = Institution.objects.create(institution_name='Archive Togo',
                                   street='somestreet',
                                   zip_code='1234',
                                   city='Lomé',
                                   country='tg',
                                   site_url='https://togoarchive.ch',
                                   institution_slug='togoarchive',
                                   created_by_id=user_stay.pk,
                                   institution_utc_add=timezone.now() - datetime.timedelta(50),)

        ref_stay = RefNumber.objects.create(holding_institution=inst_stay,
                                            ref_number_name='#1234',
                                            ref_number_title='Ref Title',
                                            collection_link='https://whatever.ch',
                                            ref_number_slug='1234',
                                            created_by_id=user_stay.pk)

        ref_go = RefNumber.objects.create(holding_institution=inst_stay,
                                          ref_number_name='#5678',
                                          ref_number_title='Ref Title 2',
                                          collection_link='https://whatever.ch',
                                          ref_number_slug='5678',
                                          created_by_id=user_stay.pk,
                                          ref_number_utc_add=timezone.now() - datetime.timedelta(50))

        author_stay = Author.objects.create(author_name='Stay',
                                            created_by_id=user_stay.pk)

        author_go = Author.objects.create(author_name='Golem',
                                          created_by_id=user_stay.pk,
                                          author_utc_add=timezone.now() - datetime.timedelta(50))

    def test_user_cleanup(self):
        self.assertEqual(User.objects.all().count(), 2)
        cleanup_users()
        self.assertEqual(User.objects.all().count(), 1)

    def test_inst_cleanup(self):
        self.assertEqual(Institution.objects.all().count(), 2)
        cleanup_inst()
        self.assertEqual(Institution.objects.all().count(), 1)

    def test_ref_cleanup(self):
        self.assertEqual(RefNumber.objects.all().count(), 2)
        cleanup_ref()
        self.assertEqual(RefNumber.objects.all().count(), 1)

    def test_author_cleanup(self):
        self.assertEqual(Author.objects.all().count(), 2)
        cleanup_author()
        self.assertEqual(Author.objects.all().count(), 1)

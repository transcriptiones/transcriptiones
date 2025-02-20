import csv

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError, DataError
from django.utils.text import slugify
from languages_plus.models import Language
from partial_date import PartialDate

from main.models import User, Document, Institution, RefNumber, Author
from main.utils import transcriptiones_slugify


class Command(BaseCommand):
    help = 'Imports batch'

    def add_arguments(self, parser):
        parser.add_argument('object_type', type=str)
        parser.add_argument('object_file', type=str)
        parser.add_argument('username', type=str)
        parser.add_argument('--use-filenames', action='store_true', help='Get transcription text from files instead of cells in documents tables')

    def handle(self, *args, **options):
        self.stdout.write('Starting batch import.')

        object_options = ['institution', 'refnumber', 'document']
        if options['object_type'] not in object_options:
            self.stdout.write(self.style.ERROR(f'"object_type" must be one of "{", ".join(object_options)}"'))

        rows = list()
        try:
            with open(options['object_file'], 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header_row = None
                row_number = 0
                for row in reader:
                    if row_number == 0:
                        header_row = row
                    else:
                        row_json = {}
                        column_number = 0
                        for column in row:
                            row_json[header_row[column_number]] = column
                            column_number += 1
                        rows.append(row_json)
                    row_number += 1
        except FileNotFoundError:
            self.stderr.write(f'Error: File {options["object_file"]} not found')
            return

        if len(rows) == 0:
            self.stderr.write(f'Error: no data found')
            return

        try:
            adding_user = User.objects.get(username=options["username"])
        except User.DoesNotExist:
            self.stderr.write(f'Error: user not found')
            return

        if options['object_type'] == 'institution':
            self.stdout.write('Trying to import institutions')
            required_keys = ("institution_name", "street", "zip_code", "city", "country", "site_url")
            for key in required_keys:
                if key not in rows[0]:
                    self.stderr.write(f'Error: column {key} not found in data')
                    return

            insts_created = 0
            insts_skipped = 0

            for new_institution in rows:
                try:
                    Institution.objects.create(institution_name=new_institution["institution_name"],
                                               street=new_institution["street"],
                                               zip_code=new_institution["zip_code"],
                                               city=new_institution["city"],
                                               country=new_institution["country"],
                                               site_url=new_institution["site_url"],
                                               created_by=adding_user,
                                               institution_slug=transcriptiones_slugify(new_institution["institution_name"], Institution, 'institution_slug'))
                    self.stdout.write(f'Created institution {new_institution["institution_name"]}')
                    insts_created += 1
                except IntegrityError as e:
                    self.stderr.write(f'Error: Failed to create: {new_institution["institution_name"]}')
                    self.stderr.write(f'Reason: {e}')
                    insts_skipped += 1

            self.stdout.write(f'{insts_created} Institutions created')
            self.stdout.write(f'{insts_skipped} Institutions skipped')

        if options['object_type'] == 'refnumber':
            self.stdout.write('Trying to import reference numbers')
            required_keys = ("holding_institution", "refnumber_name", "refnumber_title", "collection_link")
            for key in required_keys:
                if key not in rows[0]:
                    self.stderr.write(f'Error: column {key} not found in data')
                    return

            refs_created = 0
            refs_skipped = 0

            for new_refnumber in rows:
                try:
                    holding_institution = Institution.objects.get(institution_name=new_refnumber["holding_institution"])
                    RefNumber.objects.create(holding_institution=holding_institution,
                                             ref_number_name=new_refnumber["refnumber_name"],
                                             ref_number_title=new_refnumber["refnumber_title"],
                                             collection_link=new_refnumber["collection_link"],
                                             created_by=adding_user,
                                             ref_number_slug=transcriptiones_slugify(new_refnumber["refnumber_name"], RefNumber, 'ref_number_slug'))
                    self.stdout.write(f'Created RefNumber {new_refnumber["refnumber_name"]}')
                    refs_created += 1
                except IntegrityError as e:
                    self.stderr.write(f'Error: Failed to create: {new_refnumber["refnumber_name"]}')
                    self.stderr.write(f'Reason: {e}')
                    refs_skipped += 1
                except Institution.DoesNotExist:
                    self.stderr.write(f'Error: Failed to create: {new_refnumber["refnumber_name"]}')
                    self.stderr.write(f'Reason: Referenced institution does not exist')
                    refs_skipped += 1
                except DataError as e:
                    self.stderr.write(f'Error: Failed to create: {new_refnumber["refnumber_name"]}')
                    self.stderr.write(f'Reason: {e}')
                    refs_skipped += 1

            self.stdout.write(f'{refs_created} Reference Numbers created')
            self.stdout.write(f'{refs_skipped} Reference Numbers skipped')


        if options['object_type'] == 'document':
            self.stdout.write('Trying to import documents')
            required_keys = ("title_name", "parent_ref_number", "doc_start_date", "doc_end_date", "place_name",
                             "transcription_scope", "source_type_id", "transcription_text", "comments", "publish_user")
            additional_keys = ("scribes", "language")
            for key in required_keys:
                if key not in rows[0]:
                    self.stderr.write(f'Error: column {key} not found in data')
                    return

            docs_created = 0
            docs_skipped = 0

            for new_document in rows:
                try:
                    parent_ref_number = RefNumber.objects.get(ref_number_name=new_document["parent_ref_number"])
                    try:
                        end_date = PartialDate(new_document["doc_end_date"])
                    except ValidationError:
                        end_date = None

                    transcription = ''

                    if options['use_filenames']:
                        try:
                            with open(new_document["transcription_text"], mode="r", encoding="utf-8") as f:
                                transcription = f.read()
                        except FileNotFoundError as e:
                            self.stderr.write(f'Error: Failed to create: {new_document["title_name"]}')
                            self.stderr.write(f'Reason: {e}')
                            docs_skipped += 1
                            break
                    else:
                        transcription = new_document["transcription_text"]

                    the_document = Document(parent_ref_number=parent_ref_number,
                                            title_name=new_document["title_name"],
                                            doc_start_date=PartialDate(new_document["doc_start_date"]),
                                            place_name=new_document["place_name"],
                                            transcription_scope=new_document["transcription_scope"],
                                            source_type_id=new_document["source_type_id"],
                                            transcription_text=transcription,
                                            submitted_by=adding_user,
                                            document_slug=transcriptiones_slugify(new_document["title_name"], Document, 'document_slug'),
                                            commit_message='Initial commit',
                                            comments=new_document["comments"],
                                            publish_user=new_document["publish_user"],
                                            version_number=1)
                    if end_date is not None:
                        the_document.doc_end_date = end_date

                    the_document.save(trigger_notifications=False)

                    if "language" in new_document:
                        the_document.language.add(Language.objects.get(iso_639_1=new_document["language"]))

                    if "scribes" in new_document:
                        scribe_list = new_document["scribes"].split(",")
                        for scribe in scribe_list:
                            scribe = scribe.strip()
                            try:
                                author = Author.objects.get(author_name=scribe)
                            except Author.DoesNotExist:
                                author = Author.objects.create(author_name=scribe, created_by=adding_user)
                            if author is not None:
                                the_document.author.add(author)

                    self.stdout.write(f'Created Document {new_document["title_name"]}')
                    docs_created += 1
                except IntegrityError as e:
                    self.stderr.write(f'Error: Failed to create: {new_document["title_name"]}')
                    self.stderr.write(f'Reason: {e}')
                    docs_skipped += 1
                except RefNumber.DoesNotExist:
                    self.stderr.write(f'Error: Failed to create: {new_document["title_name"]}')
                    self.stderr.write(f'Reason: Referenced refnumber does not exist')
                    docs_skipped += 1
                except DataError as e:
                    self.stderr.write(f'Error: Failed to create: {new_document["title_name"]}')
                    self.stderr.write(f'Reason: {e}')
                    docs_skipped += 1

            self.stdout.write(f'{docs_created} Documents created')
            self.stdout.write(f'{docs_skipped} Documents skipped')
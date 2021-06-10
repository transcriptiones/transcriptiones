import random, os, uuid
import string

str_source_type = "INSERT INTO `main_sourcetype` (`id`, `type_name`, `parent_type_id`) " \
                  "VALUES (1, 'Main Group 1', NULL),\n (2, 'Main Group 2', NULL),\n" \
                  "(3, 'Sub Group 1-1', 1),\n (4, 'Sub Group 1-2', 1),\n" \
                  "(5, 'Sub Group 1-3', 1),\n (6, 'Sub Group 1-4', 1),\n" \
                  "(7, 'Sub Group 2-1', 2),\n (8, 'Sub Group 2-2', 2),\n" \
                  "(9, 'Sub Group 2-3', 2),\n (10, 'Sub Group 2-4', 2);\n"

str_institution = "INSERT INTO main_institution (id, institution_name, street, zip_code, " \
                  "city, country, site_url, institution_utc_add, institution_slug) VALUES"

str_ref_number = "INSERT INTO main_refnumber (id, ref_number_name, ref_number_title, collection_link, " \
                 "ref_number_utc_add, ref_number_slug, holding_institution_id) VALUES"

ref_number_idx = 1
for institution_idx in range(50):
    institution = institution_idx+1
    str_institution += f"({institution}, 'Test Institution {institution}', 'Street{institution}', '10{institution}', " \
                       f"'City{institution}', 'ch', 'http://www.dummy.ch', NOW(), 'test-institution-{institution}'),\n"

    for ref_number in range(10):
        random_number = random.randint(1000, 9999)
        str_ref_number += f"({ref_number_idx}, 'I{institution} - {random_number}', 'I{institution} RefNumber {ref_number}', 'http://www.dummy.ch', NOW(), 'i{institution}-refnumber-{ref_number}', '{institution}'),\n"
        ref_number_idx += 1

str_ref_number = str_ref_number[:-2]
str_ref_number += ";"

str_institution = str_institution[:-2]
str_institution += ";"
# print(str_institution)

authors = ['William Shakespeare',
           'Agatha Christie',
           'Barbara Cartland',
           'Danielle Steel',
           'Harold Robbins',
           'Georges Simenon',
           'Enid Blyton',
           'Sidney Sheldon',
           'J. K. Rowling',
           'Gilbert Patten',
           'Dr. Seuss',
           'Eiichiro Oda',
           'Leo Tolstoy',
           'Corín Tellado',
           'Jackie Collins',
           'Horatio Alger',
           'R. L. Stine',
           'Dean Koontz',
           'Nora Roberts',
           'Alexander Pushkin',
           'Stephen King',
           'Paulo Coelho',
           'Jeffrey Archer',
           'Louis LAmour',
           'Jirō Akagawa',
           'René Goscinny',
           'Erle Stanley Gardner']

str_authors = "INSERT INTO main_author (id, author_name, author_gnd) VALUES "
for author in authors:
    str_authors += f"(NULL, '{author}', ''),\n"

str_authors = str_authors[:-2]
str_authors += ";"

# Document generation
str_documents = ""
document_no = 1
for filename in os.listdir('dummy_texts'):
    str_documents += "INSERT INTO main_document (id, document_id, title_name, doc_start_date, doc_end_date, place_name, " \
                    "material, measurements_length, measurements_width, pages, paging_system, transcription_scope, " \
                    "comments, transcription_text, document_utc_add, document_slug, active, commit_message, " \
                    "version_number, parent_ref_number_id, source_type_id, submitted_by_id, publish_user, " \
                    "document_utc_update, illuminated, seal) VALUES "
    # random_chars = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(30))
    my_uuid = str(uuid.uuid1(random.randint(0, 281474976710655))).replace("-", "")
    with open(os.path.join('dummy_texts', filename), encoding="utf8") as f:
        lines = f.readlines()
    transcription_text = " ".join(lines)
    transcription_text = transcription_text.replace("'", "''")
    parent_ref_number = random.randint(1, 500)
    str_documents += f"(NULL, '{my_uuid}', 'Document title {document_no}', '1999-01-01 11:15:35.000000', NULL, " \
                     f"'Basel', '1', NULL, NULL, NULL, NULL, 'All things transcribed.', '', " \
                     f"'{transcription_text}', NOW(), 'document-title-{institution_idx}-{ref_number_idx}', '1', '', " \
                     f"'1', '{parent_ref_number}', '3', '1', '1', NOW(), NULL, NULL);\n"
    document_no += 1

str_documents = str_documents[:-2]
str_documents += ";"

f = open("test_db_init.sql", "w", encoding="utf8")
f.write("-- This file sets up a test database for the transcriptiones system.\n\n")
f.write("-- CLEAN DATABASE\n")
f.write("DELETE FROM main_document_author WHERE 1;\n")
f.write("DELETE FROM main_document WHERE 1;\n")
f.write("DELETE FROM main_refnumber WHERE 1;\n")
f.write("DELETE FROM main_institution WHERE 1;\n")
f.write("DELETE FROM main_author WHERE 1;\n")
f.write("DELETE FROM main_sourcetype WHERE parent_type_id IS NOT NULL;\n")
f.write("DELETE FROM main_sourcetype WHERE 1;\n\n")
f.write("-- AUTHORS\n")
f.write(str_authors)
f.write("\n\n-- SOURCE TYPES\n")
f.write(str_source_type)
f.write("\n\n-- INSTITUTIONS\n")
f.write(str_institution)
f.write("\n\n-- REF NUMBERS\n")
f.write(str_ref_number)
f.write("\n\n-- DOCUMENTS\n")
f.write(str_documents)
f.close()

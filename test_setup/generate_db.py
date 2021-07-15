import random, os, uuid

users = [(2, 'transcriber_johnny', ),
         (3, 'viola_xx69xx', ),
         (4, 'gerry_gantenbein', ),
         (5, 'dominic', ),
         (6, 'yvonne', )]

str_users = "INSERT INTO main_user (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, " \
            "`last_name`, `email`, `email_confirmed`, `is_staff`, `is_active`, `date_joined`, `mark_anonymous`, " \
            "`different_editor_subscription`, `notification_policy`, `user_orcid`, `message_notification_policy`)\n " \
            "VALUES "

for user in users:
    str_users += f"({user[0]}, '', NULL, 0, '{user[1]}', '', '', '{user[1]}@test.com', " \
                 f"'1', '0', '1', NOW(), '0', '1', '1', '0000-1234-5678', '1'),\n"

str_users = str_users[:-2]
str_users += ";"

ref_number_titles = ['Briefwechsel Mustermann - Beispilia',
                     'Gerichtsprotokoll Samson',
                     'Ratsprotokolle Musterstadt',
                     'Marktvorschriften Examplonien',
                     'Flugschriftensammlung Subversia',
                     'Gründungsurkunde Stadthausens',
                     'Gebetssprüche Kloster Frommbad']

doc_titles = ['Brief', 'Akte', 'Dokument', 'Pergament', 'Urkunde', 'Notiz']
doc_names = ['Colbert', 'Kimmel', 'Conan', 'Meyers', 'Stewart', 'Oliver']

institution_name_parts = ['Universitätsbibliothek', 'Staatsarchiv', 'Sammlung', 'Klosterarchiv', 'Stiftung']
city_names = ['Aarau', 'Basel', 'Köln', 'Duisburg', 'Einsiedeln', 'Hamburg', 'Bremen', 'Berlin', 'Wien', 'Biel', 'Winterthur', 'Zürich']
institution_names = list()
for c_name in city_names:
    for i_name in institution_name_parts:
        institution_names.append(i_name + " " + c_name)

str_source_type = "INSERT INTO `main_sourcetype` (`id`, `type_name`, `parent_type_id`) " \
                  "VALUES (1, 'Historiographische Quellen', NULL),\n " \
                  "(2, 'Hagiographische Quellen', NULL),\n" \
                  "(3, 'Rechtsquellen', NULL),\n " \
                  "(4, 'Verwaltungsschrifttum', NULL),\n" \
                  "(5, 'Korrespondenz', NULL),\n " \
                  "(6, 'Liturgische Schriften', NULL),\n" \
                  "(7, 'Wissenschaftliches Schrifttum', NULL),\n " \
                  "(8, 'Dichtung', NULL),\n" \
                  "(9, 'Politische Schriften', NULL),\n " \
                  "(10, 'Pläne / Karten', NULL),\n" \
                  "(11, 'Sonstiges', NULL),\n " \
                  "(12, 'Annalen', 1),\n " \
                  "(13, 'Chroniken', 1),\n " \
                  "(14, 'Biographien', 1),\n " \
                  "(15, 'Reiseberichte', 1),\n " \
                  "(16, 'Exempla', 1),\n " \
                  "(17, 'Geschichtsdichtung', 1),\n " \
                  "(18, 'Selbstzeugnisse', 1),\n " \
                  "(19, 'Viten', 2),\n " \
                  "(20, 'Mirakel- und Translationsberichte', 2),\n " \
                  "(21, 'Diplomatische Urkunden', 3),\n " \
                  "(22, 'Weltliche Rechtsquellen', 3),\n " \
                  "(23, 'Kirchliche Rechtsquellen', 3),\n " \
                  "(24, 'Persönliche Verträge', 3),\n " \
                  "(25, 'Urbare', 4),\n " \
                  "(26, 'Lehnbücher', 4),\n " \
                  "(27, 'Amts- und Rechnungsbücher', 4),\n " \
                  "(28, 'Bürgerbücher', 4),\n " \
                  "(29, 'Zunftakten', 4),\n " \
                  "(30, 'Matrikeln', 4),\n " \
                  "(31, 'Ratsbücher', 4),\n " \
                  "(32, 'Briefe', 5),\n " \
                  "(33, 'Postkarten', 5),\n " \
                  "(34, 'Messeregelungen', 6),\n " \
                  "(35, 'Predigten', 6),\n " \
                  "(36, 'Memorialbücher', 6),\n " \
                  "(37, 'Predigtanleitungen', 6),\n " \
                  "(38, 'Visionen', 6),\n " \
                  "(39, 'Theoretisch-theologische Schriften', 7),\n " \
                  "(40, 'Dogmatische Schriften', 7),\n " \
                  "(41, 'Enzyklopädische Schriften und Summen', 7),\n " \
                  "(42, 'Medizinische Schriften', 7),\n " \
                  "(43, 'Philosophische Schriften', 7),\n " \
                  "(44, 'Sonstige nichttheologische Fachliteratur', 7),\n " \
                  "(45, 'Epik', 8),\n " \
                  "(46, 'Lyrik', 8),\n " \
                  "(47, 'Prosa', 8),\n " \
                  "(48, 'Spiele', 8),\n " \
                  "(49, 'Traktate', 9),\n " \
                  "(50, 'Pamphlete', 9),\n " \
                  "(51, 'Allgemein', 10),\n " \
                  "(52, 'Notizen', 11);\n"

str_institution = "INSERT INTO main_institution (id, institution_name, street, zip_code, " \
                  "city, country, site_url, institution_utc_add, institution_slug) VALUES"

str_ref_number = "INSERT INTO main_refnumber (id, ref_number_name, ref_number_title, collection_link, " \
                 "ref_number_utc_add, ref_number_slug, holding_institution_id) VALUES"

ref_number_idx = 1
for institution_idx in range(50):
    institution = institution_idx+1
    str_institution += f"({institution}, '{institution_names[institution_idx]}', 'Street{institution}', '10{institution}', " \
                       f"'City{institution}', 'ch', 'http://www.dummy.ch', NOW(), 'test-institution-{institution}'),\n"

    for ref_number in range(10):
        random_number = random.randint(1000, 9999)
        random_number2 = random.randint(0, len(ref_number_titles)-1)
        str_ref_number += f"({ref_number_idx}, 'I{institution}-{random_number}-{random_number2}', '{ref_number_titles[random_number2]} {ref_number}', 'http://www.dummy.ch', NOW(), 'i{institution}-refnumber-{ref_number}', '{institution}'),\n"
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
    random_year = random.randint(1350, 1800)
    random_material = random.randint(1, 3)
    random_p_system = random.randint(1, 2)
    random_pages = random.randint(1, 30)
    random_source_type = random.randint(3, 10)
    random_illuminated = random.randint(0, 1)
    random_seal = random.randint(0, 1)
    random_number2 = random.randint(0, len(doc_titles) - 1)
    random_number3 = random.randint(0, len(doc_names) - 1)
    random_user = random.randint(1, len(users))

    str_documents += f"(NULL, '{my_uuid}', '{doc_titles[random_number2]} {doc_names[random_number3]}, {document_no}', '{random_year}-01-01 11:15:35.000000', NULL, " \
                     f"'{city_names[random.randint(0,len(city_names)-1)]}', '{random_material}', NULL, NULL, {random_pages}, {random_p_system}, 'All things transcribed.', '', " \
                     f"'{transcription_text}', NOW(), 'document-title-{document_no}', '1', 'generated', " \
                     f"'1', '{parent_ref_number}', '{random_source_type}', '{random_user}', '1', NOW(), {random_illuminated}, {random_seal});\n"
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
f.write("DELETE FROM main_sourcetype WHERE 1;\n")
f.write("DELETE FROM main_user WHERE username != 'sorin';\n\n")
f.write("-- USERS\n")
f.write(str_users)
f.write("\n\n-- AUTHORS\n")
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

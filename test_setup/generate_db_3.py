import random, os, uuid

users = [(1, 'sorin', 'sorin.marti@unibas.ch', 'A'),
         (2, 'dominic', 'd.weber@unibas.ch', 'A'),
         (3, 'yvonne', 'yfuchs@unibas.ch', 'A'),
         (4, 'transcriber_johnny', '', 'S'),
         (5, 'viola_xx69xx', '', 'S'),
         (6, 'gerry_gantenbein', '', 'S'),
         (7, 'hanging_with_my_gnomies', '', 'U'),
         (8, 'shaquille.oatmeal', '', 'U'),
         (9, 'hoosier-daddy', '', 'U' ),
         (10, 'fast_and_the_curious', '', 'U' ),
         (11, 'averagestudent', '', 'U' ),
         (12, 'BadKarma', '', 'U' ),
         (13, 'google_was_my_idea', '', 'U' ),
         (14, 'YellowSnowman', '', 'U' ),
         (15, 'AllGoodNamesRGone', '', 'U' ),
         (16, 'banana_hammock', '', 'U' ),
         (17, 'thegodfatherpart4', '', 'U' ),
         (18, 'abductedbyaliens', '', 'U' ),
         (19, 'actuallynotchrishemsworth', '', 'U' ),
         (20, 'personallyvictimizedbyreginageorge', '', 'U' ),
         (21, 'fatBatman', '', 'U' ),
         (22, 'FreddyMercurysCat', '', 'U' ),
         (23, 'ima.robot', '', 'U' ),
         (24, 'turkey_sandwich', '', 'U' ),
         (25, 'LOWERCASE_GUY', '', 'U' ),
         (26, 'ironmansnap', '', 'U' ),
         (27, 'bill_nye_the_russian_spy', '', 'U' ),
         (28, 'imma_rage_quit', '', 'U'),
         (29, 'PuppiesnKittens', '', 'U'),
         (30, 'cereal_killer', '', 'U'),
         ]

str_users = "INSERT INTO main_user (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, " \
            "`last_name`, `email`, `email_confirmed`, `is_staff`, `is_active`, `date_joined`, `mark_anonymous`, " \
            "`different_editor_subscription`, `notification_policy`, `user_orcid`, `message_notification_policy`," \
            "`ui_language`)\n " \
            "VALUES "

for user in users:
    if user[1] != 'sorin' and user[1] != 'yvonne' and user[1] != 'dominic':
        email = f'{user[1]}@host.com'
        if user[2] != '':
            email = user[2]

        isStaff = "0"
        isSuperuser = "0"
        if user[3] == 'A':
            isStaff = "1"
            isSuperuser = "1"
        if user[3] == 'S':
            isStaff = "1"

        str_users += f"({user[0]}, '', NULL, {isSuperuser}, '{user[1]}', '', '', '{email}', " \
                     f"'1', '{isStaff}', '1', NOW(), '0', '1', '1', '0000-1234-5678', '1', 'de'),\n"

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
city_names = [('Aarau', 'ch'), ('Basel', 'ch'), ('Einsiedeln', 'ch'), ('Biel', 'ch'), ('Winterthur', 'ch'),
              ('Zürich', 'ch'),
              ('Köln', 'de'), ('Duisburg', 'de'), ('Hamburg', 'de'), ('Bremen', 'de'), ('Berlin', 'de'),
              ('Wien', 'at')]
country_codes = ['ch', 'de', 'gb', 'fr']
institution_names = list()
for c_name in city_names:
    for i_name in institution_name_parts:
        institution_names.append(i_name + " " + c_name[0])

str_source_type =   "INSERT INTO `main_sourcetype` (`id`, `type_name`, `parent_type_id`, `type_name_de`, `type_name_fr`, `type_name_it`) VALUES" \
                    "(1, 'Historiographic Writings', NULL, 'Historiographische Schriften', 'Historiographic Writings', 'Historiographic Writings')," \
                    "(2, 'Religious Writings', NULL, 'Religiöse Schriften', 'Religious Writings', 'Religious Writings')," \
                    "(3, 'Legal Documents', NULL, 'Rechtsdokumente', 'Legal Documents', 'Legal Documents')," \
                    "(4, 'Administrative Writings', NULL, 'Verwaltungsschriften', 'Administrative Writings', 'Administrative Writings')," \
                    "(5, 'Correspondence', NULL, 'Korrespondenz', 'Correspondence', 'Correspondence')," \
                    "(6, 'Scholarly Writings', NULL, 'Wissenschaftliche Schriften', 'Scholarly Writings', 'Scholarly Writings')," \
                    "(7, 'Literature', NULL, 'Dichtung', 'Literature', 'Literature')," \
                    "(8, 'Political Writings', NULL, 'Politische Schriften', 'Political Writings', 'Political Writings')," \
                    "(9, 'Other Writings', NULL, 'Übrige Schriften', 'Other Writings', 'Other Writings')," \
                    "(10, 'Chronicles and Annals', 1, 'Chroniken und Annalen', 'Chronicles and Annals', 'Chronicles and Annals')," \
                    "(11, 'Ego-Documents', 1, 'Selbstzeugnisse', 'Ego-Documents', 'Ego-Documents')," \
                    "(12, 'Travelogues', 1, 'Reiseberichte', 'Travelogues', 'Travelogues')," \
                    "(13, 'History Poetry', 1, 'Geschichtsdichtung', 'History Poetry', 'History Poetry')," \
                    "(14, 'Other Historiographic Writings', 1, 'Übrige historiographische Schriften', 'Other Historiographic Writings', 'Other Historiographic Writings')," \
                    "(15, 'Hagiographic Writings', 2, 'Hagiographische Schriften', 'Hagiographic Writings', 'Hagiographic Writings')," \
                    "(16, 'Liturgic Writings', 2, 'Liturgische Schriften', 'Liturgic Writings', 'Liturgic Writings')," \
                    "(17, 'Dogmatic writings', 2, 'Dogmatische Schriften', 'Dogmatic writings', 'Dogmatic writings')," \
                    "(18, 'Sermons', 2, 'Predigten', 'Sermons', 'Sermons')," \
                    "(19, 'Memorial Writings', 2, 'Gedenkschriftgut', 'Memorial Writings', 'Memorial Writings')," \
                    "(20, 'Mystic Writings', 2, 'Mystische Schriften', 'Mystic Writings', 'Mystic Writings')," \
                    "(21, 'Other Religious Writings', 2, 'Übrige religi÷se Schriften', 'Other Religious Writings', 'Other Religious Writings')," \
                    "(22, 'Diplomatic Documents', 3, 'Diplomatische Urkunden', 'Diplomatic Documents', 'Diplomatic Documents')," \
                    "(23, 'Legal Documents of Mundane Institutions', 3, 'Rechtsdokumente weltlicher Institutionen', 'Legal Documents of Mundane Institutions', 'Legal Documents of Mundane Institutions')," \
                    "(24, 'Legal Documents of Religious Institutions', 3, 'Rechtsdokumente kirchlicher Institutionen', 'Legal Documents of Religious Institutions', 'Legal Documents of Religious Institutions')," \
                    "(25, 'Personal Contracts', 3, 'Persönliche Verträge', 'Personal Contracts', 'Personal Contracts')," \
                    "(26, 'Other Legal Documents', 3, 'Übrige Rechtsdokumente', 'Other Legal Documents', 'Other Legal Documents')," \
                    "(27, 'Property Directories', 4, 'Besitzverzeichnisse', 'Property Directories', 'Property Directories')," \
                    "(28, 'Person Directories', 4, 'Personenverzeichnisse', 'Person Directories', 'Person Directories')," \
                    "(29, 'Accounting Books', 4, 'Rechnungsbⁿcher', 'Accounting Books', 'Accounting Books')," \
                    "(30, 'Official Books', 4, 'Amtsbücher', 'Official Books', 'Official Books')," \
                    "(31, 'Other Administrative Documents', 4, 'Übrige Verwaltungsschriften', 'Other Administrative Documents', 'Other Administrative Documents')," \
                    "(32, 'Letters', 5, 'Briefe', 'Letters', 'Letters')," \
                    "(33, 'Postcards', 5, 'Postkarten', 'Postcards', 'Postcards')," \
                    "(34, 'Other Correspondence', 5, 'Übrige Korrespondenz', 'Other Correspondence', 'Other Correspondence')," \
                    "(35, 'Theoretical-theological Writings', 6, 'Theoretisch-theologische Schriften', 'Theoretical-theological Writings', 'Theoretical-theological Writings')," \
                    "(36, 'Encyclopedic Writings', 6, 'Enzyklopädische Schriften', 'Encyclopedic Writings', 'Encyclopedic Writings')," \
                    "(37, 'Scientific Writings', 6, 'Naturwissenschaftliche Schriften', 'Scientific Writings', 'Scientific Writings')," \
                    "(38, 'Philosophical Writings', 6, 'Philosophische Schriften', 'Philosophical Writings', 'Philosophical Writings')," \
                    "(39, 'Other Scholarly Writings', 6, 'Übrige wissenschaftliche Schriften', 'Other Scholarly Writings', 'Other Scholarly Writings')," \
                    "(40, 'Narrative Fiction', 7, 'Epik', 'Narrative Fiction', 'Narrative Fiction')," \
                    "(41, 'Poetry', 7, 'Lyrik', 'Poetry', 'Poetry')," \
                    "(42, 'Drama', 7, 'Dramatik', 'Drama', 'Drama')," \
                    "(43, 'Argumentative Writings', 8, 'Argumentative Schriften', 'Argumentative Writings', 'Argumentative Writings')," \
                    "(44, 'Polemic Writings', 8, 'Streitschriften', 'Polemic Writings', 'Polemic Writings')," \
                    "(45, 'Other Political Writings', 8, 'Übrige politische Schriften', 'Other Political Writings', 'Other Political Writings')," \
                    "(46, 'Others', 9, 'Übriges', 'Others', 'Others');"

str_institution = "INSERT INTO main_institution (id, institution_name, street, zip_code, " \
                  "city, country, site_url, institution_utc_add, institution_slug, created_by_id) VALUES"

str_ref_number = "INSERT INTO main_refnumber (id, ref_number_name, ref_number_title, collection_link, " \
                 "ref_number_utc_add, ref_number_slug, holding_institution_id, created_by_id) VALUES"

ref_number_idx = 1
for institution_idx in range(50):
    institution = institution_idx+1
    random_city_number = random.randint(0, len(city_names)-1)
    random_country_number = random.randint(0, len(country_codes)-1)
    random_user = random.randint(1, len(users))
    str_institution += f"({institution}, '{institution_names[institution_idx]}', 'Street{institution}', '10{institution}', " \
                       f"'{city_names[random_city_number][0]}', '{city_names[random_city_number][1]}', 'http://www.dummy.ch', NOW(), 'test-institution-{institution}', '{random_user}'),\n"

    for ref_number in range(10):
        random_number = random.randint(1000, 9999)
        random_number2 = random.randint(0, len(ref_number_titles)-1)
        random_user = random.randint(1, len(users))
        str_ref_number += f"({ref_number_idx}, 'I{institution}-{random_number}-{random_number2}', '{ref_number_titles[random_number2]} {ref_number}', 'http://www.dummy.ch', NOW(), 'i{institution}-refnumber-{ref_number}', '{institution}', '{random_user}'),\n"
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

str_authors = "INSERT INTO main_author (id, author_name, author_gnd, created_by_id) VALUES "
for author in authors:
    random_user = random.randint(1, len(users))
    str_authors += f"(NULL, '{author}', '', {random_user}),\n"

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
    random_source_type = random.randint(10, 46)
    random_illuminated = random.randint(0, 1)
    random_seal = random.randint(0, 1)
    random_anonymous = random.randint(0, 1)
    random_number2 = random.randint(0, len(doc_titles) - 1)
    random_number3 = random.randint(0, len(doc_names) - 1)
    random_user = random.randint(1, len(users))
    random_lw_value = random.randint(10, 45)
    random_lw_value_2 = random.randint(10, 45)

    str_documents += f"(NULL, '{my_uuid}', '{doc_titles[random_number2]} {doc_names[random_number3]}, {document_no}', '{random_year}-01-01 11:15:35.000000', NULL, " \
                     f"'{city_names[random.randint(0,len(city_names)-1)][0]}', '{random_material}', {random_lw_value}, {random_lw_value_2}, {random_pages}, {random_p_system}, 'All things transcribed.', '', " \
                     f"'{transcription_text}', NOW(), 'document-title-{document_no}', '1', 'generated', " \
                     f"'1', '{parent_ref_number}', '{random_source_type}', '{random_user}', '{random_anonymous}', NOW(), {random_illuminated}, {random_seal});\n"
    document_no += 1

str_documents = str_documents[:-2]
str_documents += ";"

f = open("test_db_init.sql", "w", encoding="utf8")
f.write("-- This file sets up a test database for the transcriptiones system.\n\n")
f.write("-- CLEAN DATABASE\n")
f.write("DELETE FROM main_contactmessage WHERE 1;\n")
f.write("DELETE FROM main_document_language WHERE 1;\n")
f.write("DELETE FROM main_document_author WHERE 1;\n")
f.write("DELETE FROM main_document WHERE 1;\n")
f.write("DELETE FROM main_refnumber WHERE 1;\n")
f.write("DELETE FROM main_institution WHERE 1;\n")
f.write("DELETE FROM main_author WHERE 1;\n")
f.write("DELETE FROM main_sourcetype WHERE parent_type_id IS NOT NULL;\n")
f.write("DELETE FROM main_sourcetype WHERE 1;\n")
f.write("DELETE FROM django_admin_log WHERE 1;\n")
f.write("DELETE FROM main_usermessage WHERE 1;\n")
f.write("DELETE FROM main_usernotification WHERE 1;\n")
f.write("DELETE FROM main_usersubscription WHERE 1;\n")
f.write("DELETE FROM main_user WHERE username != 'sorin' AND username != 'yvonne' AND username != 'dominic';\n\n")

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

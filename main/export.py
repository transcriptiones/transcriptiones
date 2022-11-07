import json
import re
import xml.dom.minidom
from xml.etree.ElementTree import fromstring

import pypandoc


def export(document, export_type='tei'):
    """General export function for all supported types. Takes a type argument to indicate which export function
    should be executed.
    Supported types: tei (default), json, html, pdf"""

    l_type = export_type.lower()
    if l_type not in ['txt', 'tei', 'json', 'html', 'pdf']:
        raise ValueError("export_type value is invalid")

    export_str = ""
    if l_type == 'txt':
        export_str = export_txt(document)
    if l_type == 'tei':
        export_str = export_tei(document)
    elif l_type == 'json':
        export_str = export_json(document)
    elif l_type == 'html':
        export_str = export_html(document)
    elif l_type == 'pdf':
        export_str = export_pdf(document)

    return export_str


def export_txt(document):
    text = document.transcription_text
    cleantext = re.sub(re.compile('<.*?>'), '', text)
    return cleantext


# TODO: Rewrite with DOM tree build to simplify indentation.
def export_tei(document):
    """Exports a given document within the TEI standard."""
    username = document.submitted_by.username if document.publish_user else 'Anonymous'

    illumination_text = 'There are no illuminations in this manuscript.'
    if document.illuminated:
        illumination_text = 'There are illuminations in this manuscript.'

    seal_text = 'There are no seals in this manuscript.'
    if document.seal:
        seal_text = 'There are seals in this manuscript.'

    pages_text = document.get_paging_system_display()
    if document.paging_system == 1:
        pages_text = str(document.pages) + ' page(s)'
    elif document.paging_system == 2:
        pages_text = str(document.pages) + ' folio(s)'

    doc_end_date_text = ''
    if document.doc_end_date:
        doc_end_date_text = f' notAfter="{document.doc_end_date}"'

    language_text = ''
    langs = document.language.all().values_list('iso_639_1', 'name_en')
    otherLangsIso = ''
    otherLangsName = ''
    if len(langs) > 1:
        otherLangsIso = ' otherLangs="' + ' '.join(list(zip(*langs[1:]))[0]) + '"'
        otherLangsName = ', ' + ', '.join(list(zip(*langs[1:]))[1])

    if len(langs) > 0:
        language_text = f'<textLang mainLang="{langs[0][0]}"{otherLangsIso}>{langs[0][1]}{otherLangsName}</textLang>'

    # Convert the transcription text to valid TEI
    tei_transcription = pypandoc.convert_text(document.transcription_text, 'tei', format='html')

    with open('main/templates/main/tei_template.xml') as base_file:
        text = base_file.read()
        text = text.replace('{{ SOURCE_TITLE }}', document.title_name)
        text = text.replace('{{ PARTICIPANT_LIST }}', get_xml_list('author', document.author.all().values_list('author_name', flat=True),
                                                                   number_of_spaces=28))
        text = text.replace('{{ UPLOADING_USER }}', username)
        text = text.replace('{{ DISTRIBUTOR }}', 'TRANSCRIPTIONES.CH')
        text = text.replace('{{ UPLOAD_DATE }}', document.document_utc_add.strftime('%Y-%m-%d'))
        text = text.replace('{{ UPLOAD_DATE_COMPLETE }}', document.document_utc_add.strftime('%Y-%m-%d  %H:%M:%S'))
        text = text.replace('{{ DOC_START_DATE }}', f'{document.doc_start_date}')
        text = text.replace('{{ DOC_END_DATE }}', doc_end_date_text)
        text = text.replace('{{ PLACE_NAME }}', document.place_name)
        text = text.replace('{{ LANGUAGE_LIST }}', language_text)
        text = text.replace('{{ COMMIT_MESSAGE }}', document.commit_message)
        text = text.replace('{{ EDITORIAL_COMMENTS }}', document.comments)
        text = text.replace('{{ TRANSCRIPTION_SCOPE }}', document.transcription_scope)
        text = text.replace('{{ INSTITUTION_NAME }}', document.parent_ref_number.holding_institution.institution_name)
        text = text.replace('{{ REF_NUMBER }}', document.parent_ref_number.ref_number_name)
        text = text.replace('{{ WRITING_MATERIAL }}', document.get_material_display())
        text = text.replace('{{ NUMBER_OF_PAGES }}', pages_text)
        text = text.replace('{{ DOC_HEIGHT }}', str(document.measurements_length))
        text = text.replace('{{ DOC_WIDTH }}', str(document.measurements_width))
        text = text.replace('{{ HAS_ILLUMINATIONS }}', illumination_text)
        text = text.replace('{{ HAS_SEALS }}', seal_text)
        text = text.replace('{{ TRANSCRIPTION_TEXT }}', tei_transcription)

    return text


def export_json(document):
    document_json = {
        'about': {'url': document.get_absolute_url()},
        'meta': {'title': document.title_name},
        'transcription': document.transcription_text
    }
    document_text = json.dumps(document_json, indent=2)
    return document_text


def export_html(document):
    html_transcription = pypandoc.convert_text(document.transcription_text, 'html', format='html', extra_args=['-s'])
    return html_transcription


def export_pdf(document):
    return document.transcription_text


def get_xml_list(element_name, item_list, number_of_spaces=0):
    text = ''
    loop = 0
    for item in item_list:
        if loop > 0 and number_of_spaces > 0:
            for sp in range(0,number_of_spaces):
                text += ' '
        loop += 1
        text += f'<{element_name}>{item}</{element_name}>\n'
    return text[:-1]

import json


def export(document, type='tei'):

    l_type = type.lower()
    if l_type not in ['tei', 'json', 'html', 'pdf']:
        raise ValueError("type variable value is invalid")

    export_str = ""
    if l_type == 'tei':
        export_str = export_tei(document)
    elif l_type == 'json':
        export_str = export_json(document)
    elif l_type == 'html':
        export_str = export_html(document)
    elif l_type == 'pdf':
        export_str = export_pdf(document)

    return export_str


def export_tei(document):
    tei_string = '<TEI xmlns="http://www.tei-c.org/ns/1.0">'\
                 '  <teiHeader>'\
                 '  </teiHeader>'\
                 '  <text>'\
                 '  </text>'\
                 '</TEI>'
    return tei_string


def export_json(document):
    document_json = {
        'about': {'url': document.get_absolute_url()},
        'meta': {'title': document.title_name},
        'transcription': document.transcription_text
    }
    document_text = json.dumps(document_json, indent=2)
    return document_text


def export_html(document):
    return document.transcription_text


def export_pdf(document):
    return document.transcription_text
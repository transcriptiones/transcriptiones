from django.utils.translation import ugettext as _

from main.models import Document


def title_value_list(data):
    return_list = list()
    for d in data:
        return_list.append({'title': d[0], 'value': d[1]})
    return return_list


def get_verbose_field_name(model, field_name):
    verbose_name = model._meta.get_field(field_name).verbose_name
    return verbose_name


def get_user_info(user):
    data = [(get_verbose_field_name(user, 'username'), user.username),
            (get_verbose_field_name(user, 'first_name'), user.first_name),
            (get_verbose_field_name(user, 'last_name'), user.last_name),
            (get_verbose_field_name(user, 'email'), user.email),
            (get_verbose_field_name(user, 'mark_anonymous'), user.mark_anonymous)
            ]
    return title_value_list(data)


def get_document_info_overview(document):
    data = [(get_verbose_field_name(document.parent_ref_number.holding_institution, 'institution_name'),
             document.parent_ref_number.holding_institution.institution_name),
            (get_verbose_field_name(document.parent_ref_number, 'ref_number_name'),
             document.parent_ref_number.ref_number_name),
            (get_verbose_field_name(document, 'transcription_scope'), document.transcription_scope),
            (get_verbose_field_name(document, 'document_utc_update'), document.document_utc_update),
            ]
    return title_value_list(data)


def get_document_info_metadata(document):
    data = [(get_verbose_field_name(document, 'author'),
             ", ".join(document.author.all().values_list('author_name', flat=True))),
            (get_verbose_field_name(document, 'place_name'), document.place_name),
            (get_verbose_field_name(document, 'language'),
             ", ".join(document.language.all().values_list('name_en', flat=True))),
            (get_verbose_field_name(document, 'source_type'),
             " / ".join([document.source_type.parent_type.type_name, document.source_type.type_name])),
            ]
    return title_value_list(data)


def get_document_info_manuscript(document):
    data = [(get_verbose_field_name(document, 'material'), document.material),
            (_('Measurements'), "{width:.2f} / {length:.2f} cm".format(width=document.measurements_width,
                                                                       length=document.measurements_length)),
            (get_verbose_field_name(document, 'pages'), document.pages)
            ]
    return title_value_list(data)


def get_document_info_comments(document):
    data = [(get_verbose_field_name(document, 'comments'), document.comments),
            (_('Uploaded'),
             "By {user}, on {date}".format(date=document.document_utc_update,
                                           user=document.submitted_by.username if not document.publish_user else _(
                                               'Anonymous')))
            ]

    return title_value_list(data)


# EXTENDED HELP TEXTS
def get_list(items):
    formatted_text = '<ul>'
    for item in items:
        formatted_text = formatted_text + '<li>' + item + '</li>'
    formatted_text = formatted_text + '</ul>'
    return formatted_text


def get_title_text_format(title, text):
    return "<b>{}</b><br/>{}".format(title, text)


def get_extended_help_text(model, field):
    model_name = model._meta.model_name
    help_text = 'No help text found'

    ###
    # Document
    if model_name == 'document':
        if field == 'title_name':
            help_text = get_title_text_format(_('Title of the document'), ('Use the original document\'s title if '
                                                                           'possible, use own title otherwise.'))
        elif field == 'parent_institution':
            help_text = get_title_text_format(_('Institution which holds the manuscript'), _('If the institution is '
                                                                                             'not in the list, you may '
                                                                                             'create a new one.'))
        elif field == 'parent_ref_number':
            help_text = get_title_text_format(_('Reference number as indicated by the holding institution.'),
                                              _('If the reference number is not in the list, '
                                                'you may create a new one.'))
        elif field == 'transcription_scope':
            help_text = get_title_text_format(_('Which parts of the manuscript have been transcribed?'),
                                              _('Examples {}'.format(get_list([_('Fol. 3r - 10f'), _('Chapter 10')]))))
        elif field == 'doc_start_date':
            help_text = get_title_text_format(_('Dating of the original manuscript'), _('Only the year of creation is '
                                                                                        'required. Please specify as '
                                                                                        'precise as possible.'))
        elif field == 'place_name':
            help_text = get_title_text_format(_('Place of origin'), _('Where has the document been written? '
                                                                      'Supply a city name if possible, otherwise '
                                                                      'state country or region.'))
        elif field == 'source_type':
            help_text = get_title_text_format(_('Type of the document'), _('Which type describes the nature of the '
                                                                           'described manuscript the best?'))
        elif field == 'transcription_text':
            help_text = get_title_text_format(_('Actual transcription of the manuscript'),
                                              _('You can enter the transcription directly or copy your contents'
                                                'from a Word or Excel file. Most formatting is preserved.'))
        elif field == 'author':
            help_text = get_title_text_format(_('Author(s) of the source'), _('If the author is not in the list, '
                                                                              'you may create a new one.'))
        elif field == 'language':
            help_text = get_title_text_format(_('Used languages'), _('Languages that are used in the source.'))
        elif field == 'material':
            help_text = get_title_text_format(_('Material'), _('On what material is the manuscript written?'))
        elif field == 'paging_system':
            help_text = get_title_text_format(_('What page numbering system is used?'), _('Are the pages foliated or '
                                                                                          'paginated?'))
        elif field == 'comments':
            help_text = get_title_text_format(_('Additional comments'), _('You may enter any comments on the creation '
                                                                          'of the transcription or its contents.'))
        elif field == 'illuminated':
            help_text = get_title_text_format(_('Illuminations'), _('Are there illuminations on the document?'))
        elif field == 'seal':
            help_text = get_title_text_format(_('Seals'), _('Are there any seals on the document?'))
        elif field == 'pages':
            help_text = get_title_text_format(_('Number of pages'), _('Enter the total number of pages of the source.'))
        elif field == 'publish_user':
            help_text = get_title_text_format(_('Do you want to publish anonymously?'), _('You can hide your username '
                                                                                          'on the transcription '
                                                                                          'listing if you choos so.'))
        elif field == 'commit_message':
            help_text = get_title_text_format(_('Brief description of changes'), _('Please suplly a brief description '
                                                                                   'of the changes you made. Example: '
                                                                                   '"Corrected typo", "Added authors", '
                                                                                   'etc.'))

    ###
    # Institution
    elif model_name == 'institution':
        if field == 'institution_name':
            help_text = get_title_text_format(_('Name of the institution'), _('Enter the complete name.'))
        elif field == 'street':
            help_text = get_title_text_format(_('Street Name'), _('Enter the street name with the number.'))
        elif field == 'zip_code':
            help_text = get_title_text_format(_('Zip Code'), _('Enter the zip code of the institution.'))
        elif field == 'city':
            help_text = get_title_text_format(_('City'), _('Enter the city.'))
        elif field == 'country':
            help_text = get_title_text_format(_('Country'), _('Choose the country from the drop down menu.'))
        elif field == 'site_url':
            help_text = get_title_text_format(_('Web site of the institution'), _('Enter a valid URL. Has to start '
                                                                                  'with http:// or https://'))

    ###
    # Reference Number
    elif model_name == 'refnumber':
        if field == 'holding_institution':
            help_text = get_title_text_format(_('Holding institution'), _('The institution which holds the document '
                                                                          'with this reference number.'))
        elif field == 'ref_number_name':
            help_text = get_title_text_format(_('Reference Number'), _('Reference Number as it is supplied by the '
                                                                       'institution.'))
        elif field == 'ref_number_title':
            help_text = get_title_text_format(_('Title of collection'), _('Reference numbers normally have a title. '
                                                                          'Please supply the complete title.'))
        elif field == 'collection_link':
            help_text = get_title_text_format(_('Collection link'), _('Direct link to the collection in the '
                                                                      'institution\'s catalog. Must start with http:// '
                                                                      'or https://'))

    return help_text

from uuid import UUID

import dateutil.utils
import six
from django.contrib.auth.password_validation import password_validators_help_texts, password_validators_help_text_html
from django.urls import reverse
from django.utils.functional import lazy
from django.utils.html import format_html, format_html_join, strip_tags, escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, get_language
from django.utils.text import format_lazy
from datetime import date

from main.models import Document


def title_value_list(data):
    return_list = list()
    for d in data:
        return_list.append({'title': d[0], 'value': d[1]})
    return return_list


def get_verbose_field_name(model, field_name):
    verbose_name = model._meta.get_field(field_name).verbose_name
    return _(verbose_name)


def get_author_info(author):
    data = [(get_verbose_field_name(author, 'author_name'), author.author_name)]
    # (get_verbose_field_name(author, 'author_gnd'), author.author_gnd)]
    return title_value_list(data)


def get_source_type_info(source_type):
    data = [(get_verbose_field_name(source_type, 'type_name'), source_type.type_name),
            (get_verbose_field_name(source_type, 'parent_type'), source_type.parent_type)]
    return title_value_list(data)


def get_user_info(user):
    api_key_line = ""
    api_auth_key_expired = True if user.api_auth_key_expiration and user.api_auth_key_expiration <= date.today() else False

    if user.api_auth_key is not None:
        api_key_line = mark_safe(
            user.api_auth_key + "<br>" + _(f'<small {" style=color:red" if api_auth_key_expired else ""}>({"Expired" if api_auth_key_expired else "Expires"} on {user.api_auth_key_expiration})</small>'))

    data = [(get_verbose_field_name(user, 'username'), user.username),
            (get_verbose_field_name(user, 'first_name'), user.first_name),
            (get_verbose_field_name(user, 'last_name'), user.last_name),
            (get_verbose_field_name(user, 'email'), user.email),
            (get_verbose_field_name(user, 'date_joined'), user.date_joined),
            (get_verbose_field_name(user, 'user_orcid'), user.user_orcid),
            (_('User State'), mark_safe(user.get_user_state_badge())),
            (_('Active'), mark_safe(user.get_user_activity_badge())),
            (get_verbose_field_name(user, 'mark_anonymous'),
             mark_safe('<span style="color: green;">&check;</span>') if user.mark_anonymous else mark_safe(
                 '<span style="color: red;">&cross;</span>')),
            (get_verbose_field_name(user, 'api_auth_key'), api_key_line)
            ]
    return title_value_list(data)


def get_public_user_info(user):
    data = [(get_verbose_field_name(user, 'username'), user.username),
            (get_verbose_field_name(user, 'user_orcid'), user.user_orcid),
            (_('Year joined'), user.date_joined.year),
            (_('Active'), mark_safe(user.get_user_activity_badge())),
            ]
    return title_value_list(data)


def get_institution_info(institution):
    data = [(get_verbose_field_name(institution, 'street'), institution.street),
            (_('Zip / City'), f"{institution.zip_code} / {institution.city}"),
            (get_verbose_field_name(institution, 'country'), institution.country.name),
            (get_verbose_field_name(institution, 'site_url'),
             mark_safe(f'<a href="{institution.site_url}" target="_blank">{institution.site_url}</a>'))
            ]
    return title_value_list(data)


def get_ref_number_info(ref_number):
    data = [(get_verbose_field_name(ref_number, 'holding_institution'),
             mark_safe(
                 f'<a href="{ref_number.holding_institution.get_absolute_url()}">{ref_number.holding_institution.institution_name}</a>')),
            (get_verbose_field_name(ref_number, 'ref_number_name'), ref_number.ref_number_name),
            (get_verbose_field_name(ref_number, 'ref_number_title'), ref_number.ref_number_title),
            (get_verbose_field_name(ref_number, 'collection_link'),
             mark_safe(f'<a href="{ref_number.collection_link}" target="_blank">{ref_number.collection_link}</a>'))
            ]
    return title_value_list(data)


def get_last_change_string(document):
    if document.publish_user:
        profile_url = reverse("main:public_profile", kwargs={"username": document.submitted_by.username})
        update_text = mark_safe(format_lazy(_('<small>by <a href="{profile_url}">{submitted_by}</a> at {time}</small>'),
                                profile_url=profile_url, submitted_by=document.submitted_by,
                                time=document.document_utc_add.strftime("%Y-%m-%d %H:%M:%S")))
    else:
        update_text = mark_safe(format_lazy(_('<small>by anonymous at {time}</small>'),
                                            time=document.document_utc_add.strftime("%Y-%m-%d %H:%M:%S")))
    return update_text


def get_upload_string(document):
    initial_doc = Document.all_objects.get(document_id=document.document_id, version_number=1)
    return get_last_change_string(initial_doc)


def get_version_url_string(document, request):
    url = f"{request.scheme}://{request.get_host()}{document.get_absolute_version_url()}"
    url_text = format_html('<small>{} <i class="fas fa-clipboard" title="{}" id="toclipboard" data-copy="{}"></i></small>', url, _('Copy to clipboard'), url)
    return url_text


def get_document_info_overview(document):
    data = [(get_verbose_field_name(document.parent_ref_number.holding_institution, 'institution_name'),
             mark_safe(
                 f'<a href="{document.parent_ref_number.holding_institution.get_absolute_url()}">{document.parent_ref_number.holding_institution.institution_name}</a>')),
            (get_verbose_field_name(document.parent_ref_number, 'ref_number_name'),
             mark_safe(
                 f'<a href="{document.parent_ref_number.get_absolute_url()}">{document.parent_ref_number.ref_number_name}</a>')),
            (get_verbose_field_name(document, 'transcription_scope'), document.transcription_scope),
            (_("Last Change"), get_last_change_string(document)),
            (_("Initial Upload"), get_upload_string(document)),
            ]
    return title_value_list(data)


def get_document_meta_edit_info(document):
    updating_user = _("Anonymous")
    data = [(get_verbose_field_name(document.parent_ref_number.holding_institution, 'institution_name'),
             mark_safe(
                 f'<a href="{document.parent_ref_number.holding_institution.get_absolute_url()}">{document.parent_ref_number.holding_institution.institution_name}</a>')),
            (get_verbose_field_name(document.parent_ref_number, 'ref_number_name'),
             mark_safe(
                 f'<a href="{document.parent_ref_number.get_absolute_url()}">{document.parent_ref_number.ref_number_name}</a>')),
            (_("Last Change"), get_last_change_string(document)),
            (_("Initial Upload"), get_upload_string(document)),
            ]
    return title_value_list(data)


def get_document_info_metadata(document):
    author_list = document.author.all()
    formatted_author_list = list()
    for a in author_list:
        formatted_author_list.append(f'<a href="{a.get_absolute_url()}">{a.author_name}</a>')
    period_string = f"{document.doc_start_date}"
    if document.doc_end_date is not None:
        period_string += f" - {document.doc_end_date}"

    data = [(get_verbose_field_name(document, 'author'), mark_safe(", ".join(formatted_author_list))),
            (get_verbose_field_name(document, 'place_name'), document.place_name),
            (_("Creation Period"), period_string),
            (get_verbose_field_name(document, 'language'),
             ", ".join(document.language.all().values_list('name_native', flat=True))),
            (get_verbose_field_name(document, 'source_type'),
             mark_safe(" / ".join([
                                      f'<a href="{document.source_type.parent_type.get_absolute_url()}">{document.source_type.parent_type.get_translated_name(get_language())}</a>',
                                      f'<a href="{document.source_type.get_absolute_url()}">{document.source_type.get_translated_name(get_language())}</a>']))),
            ]
    return title_value_list(data)


def get_document_info_manuscript(document):
    doc_width = document.measurements_width
    doc_length = document.measurements_length
    if doc_width is None:
        doc_width = 0.0
    if doc_length is None:
        doc_length = 0.0

    data = [(get_verbose_field_name(document, 'material'), document.get_material_display()),
            (_('Measurements'), "{width:.2f} / {length:.2f} cm".format(width=doc_width,
                                                                       length=doc_length) + " " + _("(w/h)")),
            (get_verbose_field_name(document, 'pages'), document.pages),
            (get_verbose_field_name(document, 'paging_system'), document.get_paging_system_display()),
            (get_verbose_field_name(document, 'seal'),
             mark_safe('<span style="color: green;">&check;</span>') if document.seal else mark_safe(
                 '<span style="color: red;">&cross;</span>')),
            (get_verbose_field_name(document, 'illuminated'),
             mark_safe('<span style="color: green;">&check;</span>') if document.illuminated else mark_safe(
                 '<span style="color: red;">&cross;</span>'))
            ]
    return title_value_list(data)


def get_document_info_comments(document):
    if document.publish_user:
        user = f'<a href="{document.submitted_by.get_absolute_url()}">{document.submitted_by.username}</a>'
    else:
        user = _('Anonymous')
    date = document.document_utc_update

    data = [(get_verbose_field_name(document, 'comments'), document.comments),
            ]

    return title_value_list(data)


# EXTENDED HELP TEXTS
def get_title_text_format(title, text):
    """Formats the title of a tooltip"""
    return format_lazy('<b>{title}</b><br/>{text}', title=title, text=text)
    # return "<b>{}</b><br/>{}".format(title, text)


def _get_password_validator_text_format(password_validators=None):
    help_texts = password_validators_help_texts(password_validators)
    help_items = format_html_join(' ', '{}', ((help_text,) for help_text in help_texts))
    return help_items


get_password_validator_text_format = lazy(_get_password_validator_text_format, str)


def get_extended_help_text(model, field):
    """Form fields have an extended help text with more information on what to put in the field. Those help texts are
    managed here."""
    model_name = model._meta.model_name
    help_text = _('No help text found')
    ###
    # Document
    if model_name == 'document':
        if field == 'title_name':
            help_text = get_title_text_format(_('Title of the document'), _('Title of the source document, which is '
                                                                            'transcribed here. Use the original '
                                                                            'document\'s title if possible, use an own '
                                                                            'title otherwise.'))
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
                                              _('E. g.: Entire Document, Fol. 3r - 10v, Chapter 10'))
        elif field == 'doc_start_date':
            help_text = get_title_text_format(_('Earliest creation date of the original manuscript'),
                                              _('Only the year of creation is required. Please specify as precisely as '
                                                'possible.'))
        elif field == 'doc_end_date':
            help_text = get_title_text_format(_('Latest creation date of the original manuscript'),
                                              _('Optional field. Only the year of creation is required. Please specify '
                                                'as precisely as possible.'))
        elif field == 'place_name':
            help_text = get_title_text_format(_('Place of origin'), _('Where has the document been written? '
                                                                      'Supply a city name if possible, otherwise '
                                                                      'use country or region.'))
        elif field == 'selection_helper_source_type':
            help_text = get_title_text_format(_('Type of the document'), _('Which type best describes the source? '
                                                                           'First level of categorization.'))
        elif field == 'source_type':
            help_text = get_title_text_format(_('Type of the document'), _('Which type best describes the source? '
                                                                           'Second level of categorization. '
                                                                           'Select a parent source type before filling '
                                                                           'out this field.'))
        elif field == 'transcription_text':
            help_text = get_title_text_format(_('Transcription of the manuscript'),
                                              _('You can enter the transcription directly or copy your contents'
                                                'from a Word or Excel file. Most formatting is preserved.'))
        elif field == 'author':
            help_text = get_title_text_format(_('Scribe(s) of the source'), _('If a scribe is not in the list, '
                                                                              'you may create a new one.'))
        elif field == 'language':
            help_text = get_title_text_format(_('Used languages'), _('Languages that are used in the source.'))
        elif field == 'material':
            help_text = get_title_text_format(_('Material'), _('Optional field. On what material is the manuscript written?'))
        elif field == 'paging_system':
            help_text = get_title_text_format(_('What page numbering system is used?'), _('Optional field. Are the pages foliated or '
                                                                                          'paginated?'))
        elif field == 'comments':
            help_text = get_title_text_format(_('Additional comments'), _('Optional field. You may enter any comments on the creation '
                                                                          'of the transcription or its contents. Here, you may also place '
                                                                          'links to external resources such as digitizations or editions '
                                                                          'of the source.'))
        elif field == 'illuminated':
            help_text = get_title_text_format(_('Illuminations'), _('Optional field. Are there illuminations on the document?'))
        elif field == 'seal':
            help_text = get_title_text_format(_('Seals'), _('Optional field. Are there any seals on the document?'))
        elif field == 'pages':
            help_text = get_title_text_format(_('Number of pages'), _('Optional field. Enter the total number of pages of the source.'))
        elif field == 'publish_user':
            help_text = get_title_text_format(_('Do you want to publish anonymously?'), _('You can hide your username '
                                                                                          'on the transcription '
                                                                                          'listing if you choose so.'))
        elif field == 'commit_message':
            help_text = get_title_text_format(_('Brief description of changes'), _('Please supply a brief description '
                                                                                   'of the changes you made. Examples: '
                                                                                   'Corrected typo, Added scribes, '
                                                                                   'etc.'))
        elif field == 'measurements_length':
            help_text = get_title_text_format(_('Length of the document'), _('Optional field. Please write down the length '
                                                                             '(top to bottom) in centimeters.'))
        elif field == 'measurements_width':
            help_text = get_title_text_format(_('Width of the document'), _('Optional field. Please write down the width (left to '
                                                                            'right) in centimeters.'))

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
            help_text = get_title_text_format(_('Web site of the institution'), _('Optional Field. Enter a valid URL. Must start '
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
            help_text = get_title_text_format(_('Title of collection'), _('Reference numbers usually have a title. '
                                                                          'Please supply the complete title. '
                                                                          'If the institution does not supply a title '
                                                                          'for this reference number, you may supply '
                                                                          'an own descriptive title. Please note '
                                                                          'that this might not be the same as the '
                                                                          'title of the transcribed document.'))
        elif field == 'collection_link':
            help_text = get_title_text_format(_('Collection link'), _('Optional Field. Direct link to the collection in '
                                                                      'the institution\'s catalog. Must start with http:// '
                                                                      'or https://'))

    ###
    # User
    elif model_name == 'user':
        if field == 'username':
            help_text = get_title_text_format(_('Username'), _('The name must be unique and can\'t contain any special '
                                                               'characters. It will be shown to other users.'))
        elif field == 'first_name':
            help_text = get_title_text_format(_('First name'), _('Your given name. This information will not be public.'))
        elif field == 'last_name':
            help_text = get_title_text_format(_('Last name'), _('Your family name. This information will not be public.'))
        elif field == 'email':
            help_text = get_title_text_format(_('Email address'), _('You must choose a valid address. It is used to '
                                                                    'verify your information and activate your '
                                                                    'account. This information will not be public.'))
        elif field == 'mark_anonymous':
            help_text = get_title_text_format(_('Anonymous publishing'), _('Your documents can be published '
                                                                           'anonymously by default. You can change '
                                                                           'this setting any time.'))
        elif field == 'user_orcid':
            help_text = get_title_text_format(_('ORCID'), _('Optional Field. ORCID provides a persistent digital identifier that you '
                                                            'own and control, and that distinguishes you from every '
                                                            'other researcher.'))
        elif field == 'ui_language':
            help_text = get_title_text_format(_('Default website language'), _('Choose the default language in which '
                                                                               'the transcriptiones web interface '
                                                                               'will be presented to you. You can '
                                                                               'change the language at any time.'))
        elif field == 'password1' or field == 'new_password1':
            help_text = get_title_text_format(_('Password'), get_password_validator_text_format())
        elif field == 'password2' or field == 'new_password2':
            help_text = get_title_text_format(_('Confirm password'), _('Enter the password again for confirmation.'))
        elif field == 'old_password':
            help_text = get_title_text_format(_('Your old password'), _('Enter your old password for verification.'))

    return help_text

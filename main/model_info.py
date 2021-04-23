from django.utils.translation import ugettext as _


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
    data = [(get_verbose_field_name(document.parent_ref_number.holding_institution, 'institution_name'), document.parent_ref_number.holding_institution.institution_name),
            (get_verbose_field_name(document.parent_ref_number, 'ref_number_name'), document.parent_ref_number.ref_number_name),
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
                                           user=document.submitted_by.username if not document.publish_user else _('Anonymous')))
            ]

    return title_value_list(data)
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

from django.urls import reverse


def get_document_subscription_message(user, document):
    text = f'Hi {user.username}\n\n' \
           f'The document {document.title_name} has changed.\n\n' \
           f'View the the document: <a href="{document.get_absolute_url()}">here</a>\n' \
           f'Manage your subscriptions: <a href="{reverse("main:subscriptions")}">here</a>\n\n' \
           f'Best regards from the Transcriptiones Team'
    return text


def get_reference_subscription_message(user, ref_number):
    text = f'Hi {user.username}\n\n' \
           f'Documents with the reference number {ref_number.ref_number_name} have changed.\n\n' \
           f'View the the reference number: <a href="{ref_number.get_absolute_url()}">here</a>\n' \
           f'Manage your subscriptions: <a href="{reverse("main:subscriptions")}">here</a>\n\n' \
           f'Best regards from the Transcriptiones Team'
    return text


def get_user_subscription_message(subscribing_user, user):
    text = f'Hi {subscribing_user.username}\n\n' \
           f'The user {user.username} has changed data.\n\n' \
           f'View the the users activity: <a href="{reverse("main:")}">here</a>\n' \
           f'Manage your subscriptions: <a href="{reverse("main:subscriptions")}">here</a>\n\n' \
           f'Best regards from the Transcriptiones Team'
    return text

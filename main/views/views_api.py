from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render

from main.export import export
import main.api_v1 as api_v1
from main.models import Document, User

APIS = {"v1": api_v1}


def check_authentication_and_version(request, api_version):
    api_auth_key = request.GET.get("auth", None)

    # Check if parameter is set
    if api_auth_key is None:
        return HttpResponse("TRANSCRIPTIONES API ERROR: No authentication", content_type='text/plain')
    # Check if parameter value is in DB
    try:
        api_user = User.objects.get(api_auth_key=api_auth_key)
    except User.DoesNotExist:
        return HttpResponse("TRANSCRIPTIONES API ERROR: Invalid authentication", content_type='text/plain')

    # Check if the key is still valid
    if api_user.api_auth_key_expiration <= datetime.today().date():
        return HttpResponse("TRANSCRIPTIONES API ERROR: Expired authentication", content_type='text/plain')

    if api_version not in APIS:
        return HttpResponse("TRANSCRIPTIONES API ERROR: Invalid Version. Must be /v1/", content_type='text/plain')


def api_view(request, api_version, api_request):
    response = check_authentication_and_version(request, api_version)
    if response is not None:
        return response

    response = APIS[api_version].check_request(api_version, api_request)
    if response is not None:
        return response

    response = APIS[api_version].get_api_response(request, api_request)
    return response


def api_detail_view(request, api_version, api_request, object_id):
    response = check_authentication_and_version(request, api_version)
    if response is not None:
        return response

    response = APIS[api_version].check_request(api_version, api_request)
    if response is not None:
        return response

    response = APIS[api_version].get_api_object_response(request, api_request, object_id)
    return response


def api_tei_export_view(request, api_version, object_id):
    response = check_authentication_and_version(request, api_version)
    if response is not None:
        return response

    document = Document.objects.get(id=object_id)
    file_contents = export(document, export_type='tei')
    return HttpResponse(file_contents, content_type='text/plain')


def api_plain_export_view(request, api_version, object_id):
    response = check_authentication_and_version(request, api_version)
    if response is not None:
        return response

    document = Document.objects.get(id=object_id)
    file_contents = export(document, export_type='txt')
    return HttpResponse(file_contents, content_type='text/plain')


def api_doc_view(request):
    return render(request, 'main/info/api_documentation.html')
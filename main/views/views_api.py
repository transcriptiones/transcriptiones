from django.http import HttpResponse
from django.shortcuts import render

import main.api_v1 as api_v1

APIS = {"v1": api_v1}


def api_view(request, api_version, api_request):
    if api_version not in APIS:
        return HttpResponse("Invalid Version. Must be /v1/", content_type='text/plain')

    response = APIS[api_version].check_request(api_version, api_request)
    if response is not None:
        return response

    response = APIS[api_version].get_api_response(request, api_request)
    return response


def api_detail_view(request, api_version, api_request, object_id):
    if api_version not in APIS:
        return HttpResponse("Invalid Version. Must be /v1/", content_type='text/plain')

    response = APIS[api_version].check_request(api_version, api_request)
    if response is not None:
        return response

    response = APIS[api_version].get_api_object_response(request, api_request, object_id)
    return response

def api_doc_view(request):
    return render(request, 'main/info/api_documentation.html')
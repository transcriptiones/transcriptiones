import json
from datetime import datetime

from django.core.paginator import Paginator
from django.http import HttpResponse
from django.urls import reverse

from main.models import Document, Institution, RefNumber, SourceType

REQUESTS = ("institutions", "refnumbers", "sourcetypes", "documents")


def get_error_response(error_msg, details=None):
    result = "TRANSCRIPTIONES API ERROR: " + error_msg + "\n"
    result += " Valid Command Structure: /<version>/<request>/?param=value"
    if details is not None:
        result += "\n           Error Details: " + details + "\n\n\n---\n"\
                  "(Get more Information about the TRANSCRIPTIONES API: [URL])"
    return HttpResponse(result, content_type='text/plain')


def check_request(api_version, api_request):
    # Check API request
    if api_request not in REQUESTS:
        return get_error_response("Invalid Request",
                                  details=f"<request> must be one of: [{', '.join(REQUESTS)}]")
    return None


def create_response_json(request):
    return {
        'request': {
            'api': 'Transcriptiones API',
            'documentation': request.build_absolute_uri(reverse('main:api_doc_view')),
            'api-version': 'v1',
            'requested-at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }}


def get_api_response(request, api_request):
    version = "v1"
    response_json = create_response_json(request)

    page_number = int(request.GET.get('page', 1))
    query = request.GET.get('query', None)
    level = request.GET.get('level', None)
    institution = request.GET.get('institution', None)
    refnumber = request.GET.get('refnumber', None)
    sourcetype = request.GET.get('sourcetype', None)
    user_name = request.GET.get('user', None)

    # Get object list
    # Institution
    if api_request == REQUESTS[0]:
        object_list = Institution.objects.all().order_by('institution_name')
        if query is not None:
            object_list = object_list.filter(institution_name__icontains=query)
    # Reference Number
    elif api_request == REQUESTS[1]:
        object_list = RefNumber.objects.all().order_by('ref_number_title')
        if query is not None:
            object_list = object_list.filter(ref_number_title__icontains=query)
        if institution is not None:
            object_list = object_list.filter(holding_institution_id=int(institution))
    # Source Type
    elif api_request == REQUESTS[2]:
        object_list = SourceType.objects.all().order_by('type_name')
        if query is not None:
            object_list = object_list.filter(type_name__icontains=query)
        if level == "top":
            object_list = object_list.filter(parent_type=None)
        if level == "bottom":
            object_list = object_list.exclude(parent_type=None)
    # Document
    elif api_request == REQUESTS[3]:
        object_list = Document.objects.all().order_by('title_name')
        if query is not None:
            object_list = object_list.filter(title_name__icontains=query)
        if institution is not None:
            object_list = object_list.filter(parent_ref_number__holding_institution_id=int(institution))
        if refnumber is not None:
            object_list = object_list.filter(parent_ref_number_id=int(refnumber))
        if sourcetype is not None:
            object_list = object_list.filter(source_type_id=int(sourcetype))
        if user_name is not None:
            object_list = object_list.filter(submitted_by__username=user_name)

    else:
        return get_error_response("Invalid Request")

    paginator = Paginator(object_list, 10)
    if 0 < page_number <= paginator.num_pages:
        page = paginator.page(page_number)
    else:
        return get_error_response("Invalid Page Number", details="The page number is out of bounds")

    response_json["num-results"] = paginator.count
    response_json["num-pages"] = paginator.num_pages
    response_json["page"] = page.number
    response_json["result-list"] = []

    for result in page:
        result_object = result.get_api_list_json()
        result_object["url"] = request.build_absolute_uri(result_object["url"])
        result_object["api-request"] = request.build_absolute_uri(result_object["api-request"])
        response_json["result-list"].append(result_object)

        """if api_request == REQUESTS[2]:
            result_object['name'] = result.type_name
            result_object['parent-type'] = "None (top level)"
            if result.parent_type is not None:
                result_object['parent-type'] = result.parent_type.type_name"""

    json_object = json.dumps(response_json)
    return HttpResponse(json_object, content_type='text/plain')


def get_api_object_response(request, api_request, object_id):
    response_json = create_response_json(request)

    # Get object
    if api_request == REQUESTS[0]:
        api_object = Institution.objects.get(id=object_id)
    elif api_request == REQUESTS[1]:
        api_object = RefNumber.objects.get(id=object_id)
    elif api_request == REQUESTS[2]:
        api_object = SourceType.objects.get(id=object_id)
    elif api_request == REQUESTS[3]:
        api_object = Document.all_objects.get(id=object_id)
    else:
        return get_error_response("Invalid Request")
    detail_json = api_object.get_api_detail_json()
    url_updates = ("refnumbers", "documents")
    for update in url_updates:
        if update in detail_json.keys():
            for update_item in detail_json[update]:
                update_item["api-request"] = request.build_absolute_uri(update_item["api-request"])
    response_json.update(detail_json)
    json_object = json.dumps(response_json)
    return HttpResponse(json_object, content_type='text/plain')

import json
from datetime import datetime

from django.core.paginator import Paginator
from django.http import HttpResponse
from django.urls import reverse

from main.models import Document, Institution, RefNumber, SourceType

REQUESTS = ("institutions", "refnumbers", "sourcetypes", "documents")


def get_error_response(error_msg, details=None):
    result = "TRANSCIPTIONES API ERROR: " + error_msg + "\n"
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

    # Get object list
    if api_request == REQUESTS[0]:
        object_list = Institution.objects.all().order_by('institution_name')
        if query is not None:
            object_list = object_list.filter(institution_name__icontains=query)
    elif api_request == REQUESTS[1]:
        object_list = RefNumber.objects.all().order_by('ref_number_title')
        if query is not None:
            object_list = object_list.filter(ref_number_title__icontains=query)
    elif api_request == REQUESTS[2]:
        object_list = SourceType.objects.all().order_by('type_name')
        if query is not None:
            object_list = object_list.filter(type_name__icontains=query)
        if level == "top":
            object_list = object_list.filter(parent_type=None)

    elif api_request == REQUESTS[3]:
        object_list = Document.objects.all().order_by('title_name')
        if query is not None:
            object_list = object_list.filter(title_name__icontains=query)
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
        result_object = {'id': result.id,
                         'url': request.build_absolute_uri(result.get_absolute_url()),
                         'api-request': f'/api/v1/{api_request}/{result.id}/'}

        if api_request == REQUESTS[0]:
            result_object['name'] = result.institution_name
            result_object['ref-numbers'] = result.refnumber_set.count()
            result_object['documents'] = Document.objects.filter(parent_ref_number__in=result.refnumber_set.all()).count()
        elif api_request == REQUESTS[1]:
            result_object['name'] = result.ref_number_name
            result_object['title'] = result.ref_number_title
        elif api_request == REQUESTS[2]:
            result_object['name'] = result.type_name
            result_object['parent-type'] = "None (top level)"
            if result.parent_type is not None:
                result_object['parent-type'] = result.parent_type.type_name
        elif api_request == REQUESTS[3]:
            result_object['name'] = result.title_name
        else:
            return get_error_response("Invalid Request")
        response_json["result-list"].append(result_object)

    json_object = json.dumps(response_json)
    return HttpResponse(json_object, content_type='text/plain')


def get_api_object_response(request, api_request, object_id):
    response_json = create_response_json(request)
    try:
        institution = Institution.objects.get(id=object_id)
    except Institution.DoesNotExist:
        return get_error_response("Institution ID does not exist")

    response_json.update( {
                    'id': institution.id,
                    'name': institution.institution_name,
                    'url': request.build_absolute_uri(institution.get_absolute_url()),
                    'ref-numbers': institution.refnumber_set.count(),
                    'documents': Document.objects.filter(parent_ref_number__in=institution.refnumber_set.all()).count()
                })
    response_json['document-ids'] = list(Document.objects.filter(parent_ref_number__in=institution.refnumber_set.all()).values_list('pk', flat=True))
    json_object = json.dumps(response_json)
    return HttpResponse(json_object, content_type='text/plain')

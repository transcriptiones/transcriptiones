from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers
from main import models
import zipfile
import os


@user_passes_test(lambda u: u.is_superuser)
def admin_view(request):
    """Shows a static page with options of an admin user."""
    return render(request, 'main/admin/admin.html')


@user_passes_test(lambda u: u.is_superuser)
def admin_statistics_view(request):

    return render(request, 'main/admin/statistics.html')


@user_passes_test(lambda u: u.is_superuser)
def admin_merge_docs_view(request):
    return render(request, 'main/admin/merge_docs.html')


@user_passes_test(lambda u: u.is_superuser)
def admin_export_json_view(request):
    file_name = "transcriptiones.zip"
    zip_file = zipfile.ZipFile(file_name, mode="w", compression=zipfile.ZIP_DEFLATED)

    data_source_type = serializers.serialize("json", models.SourceType.objects.all())
    zip_file.writestr("SourceType.json", data_source_type)

    data_author = serializers.serialize("json", models.Author.objects.all())
    zip_file.writestr("Author.json", data_author)

    data_documents = serializers.serialize("json", models.Document.objects.all())
    zip_file.writestr("Document.json", data_documents)

    data_institutions = serializers.serialize("json", models.Institution.objects.all())
    zip_file.writestr("Institution.json", data_institutions)

    data_ref_numbers = serializers.serialize("json", models.RefNumber.objects.all())
    zip_file.writestr("RefNumber.json", data_ref_numbers)

    zip_file.close()

    response = HttpResponse(open(file_name, 'rb'), content_type="application/zip")
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    os.remove(file_name)
    return response



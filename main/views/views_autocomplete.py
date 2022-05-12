import json

from dal import autocomplete
from django.db.models import Q
from django.utils.html import format_html
from django.http import HttpResponse
from django.utils.translation import get_language

from main.models import Institution, RefNumber, SourceType, Author, Language


def institution_id_view(request):
    inst = Institution.objects.all().order_by('-institution_utc_add')[0]
    return HttpResponse(json.dumps({"id": str(inst.pk),
                                    "text": str(inst.institution_name),
                                    "selected_text": str(inst.institution_name)}), content_type='application/json')


def refnumber_id_view(request):
    refn = RefNumber.objects.all().order_by('-ref_number_utc_add')[0]
    return HttpResponse(json.dumps({"id": str(refn.pk),
                                    "text": f"{refn.ref_number_title} - {refn.ref_number_name}",
                                    "selected_text": f"{refn.ref_number_title} - {refn.ref_number_name}"}),
                        content_type='application/json')


def ref_number_id_view(request, ref_id):
    refn = RefNumber.objects.get(pk=ref_id)
    return HttpResponse(json.dumps({"id": str(refn.pk),
                                    "text": f"{refn.ref_number_title} - {refn.ref_number_name}",
                                    "selected_text": f"{refn.ref_number_title} - {refn.ref_number_name}"}),
                        content_type='application/json')


class InstitutionAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete View for Institutions. Used for autocomplete dropdown in upload form. Queryset gets ordered by
    the institution's name."""

    def get_queryset(self):
        qs = Institution.objects.all().order_by('institution_name')
        if self.q:
            qs = qs.filter(institution_name__icontains=self.q)
        return qs


class RefNumberAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete View for Reference Numbers. Used for autocomplete dropdown in upload form. Queryset gets ordered by
    the ref numbers's name. Needs a preselected institution in order to work."""

    def get_result_label(self, result):
        return f"{result.ref_number_name} - {result.ref_number_title}"

    def get_selected_result_label(self, result):
        return f"{result.ref_number_name} - {result.ref_number_title}"

    def get_queryset(self):
        qs = RefNumber.objects.all().order_by('ref_number_name')
        selected_institution = self.forwarded.get('parent_institution', None)

        if not selected_institution:
            return []
        else:
            qs = qs.filter(holding_institution=selected_institution)

        if self.q:
            qs = qs.filter(Q(ref_number_title__icontains=self.q) | Q(ref_number_name__icontains=self.q) )
        return qs


class SourceTypeAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete View for Source Type parents. """

    def get_result_label(self, result):
        language = get_language()
        return format_html('{}<br/><small>{}</small>',
                           result.get_translated_name(language),
                           result.get_translated_description(language))

    def get_selected_result_label(self, result):
        language = get_language()
        return result.get_translated_name(language)

    def get_queryset(self):
        qs = SourceType.objects.filter(parent_type=None).order_by('type_name')

        if self.q:
            qs = qs.filter(type_name__icontains=self.q)
        return qs


class SourceTypeChildAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete View for Source Type children.  Needs a preselected parent source type in order to work."""

    def get_result_label(self, result):
        language = get_language()
        return format_html('{}<br/><small>{}</small>',
                           result.get_translated_name(language),
                           result.get_translated_description(language))

    def get_selected_result_label(self, result):
        language = get_language()
        return result.get_translated_name(language)

    def get_queryset(self):
        qs = SourceType.objects.exclude(parent_type=None).order_by('type_name')
        selected_parent_type = self.forwarded.get('selection_helper_source_type', None)

        if not selected_parent_type:
            return []
        else:
            qs = qs.filter(parent_type=selected_parent_type)

        if self.q:
            qs = qs.filter(type_name__icontains=self.q)
        return qs


class AuthorAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete View for Authors"""

    def get_queryset(self):
        qs = Author.objects.all().order_by('author_name')

        if self.q:
            qs = qs.filter(author_name__icontains=self.q)
        return qs

    def create_object(self, text):
        return Author.objects.create(author_name=text, created_by=self.request.user)


class LanguageAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete View for Languages"""

    def get_queryset(self):
        qs = Language.objects.all().order_by('name_native')

        if self.q:
            qs = qs.filter(Q(name_native__icontains=self.q) | Q(name_en__icontains=self.q))
        return qs

    def get_result_label(self, result):
        return f"{result.name_native} ({result.name_en})"

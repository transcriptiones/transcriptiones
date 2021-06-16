from dal import autocomplete
from main.models import Institution, RefNumber, SourceType, Author, Language


class InstitutionAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete View for Institutions"""

    def get_queryset(self):
        qs = Institution.objects.all()
        if self.q:
            qs = qs.filter(institution_name__icontains=self.q)

        return qs


class RefNumberAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete View for Ref Numbers"""

    def get_queryset(self):
        qs = RefNumber.objects.all()
        selected_institution = self.forwarded.get('parent_institution', None)
        print(selected_institution)

        if not selected_institution:
            return []
        else:
            qs = qs.filter(holding_institution=selected_institution)

        if self.q:
            qs = qs.filter(ref_number_title__icontains=self.q, ref_number_name__icontains=self.q)

        return qs


class SourceTypeAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete View for Source Type parents"""

    def get_queryset(self):
        qs = SourceType.objects.filter(parent_type=None)

        if self.q:
            qs = qs.filter(type_name__icontains=self.q)

        return qs


class SourceTypeChildAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete View for Source Type children"""

    def get_queryset(self):
        qs = SourceType.objects.exclude(parent_type=None)
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
        qs = Author.objects.all()

        if self.q:
            qs = qs.filter(author_name__icontains=self.q)

        return qs


class LanguageAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete View for Languages"""

    def get_queryset(self):
        qs = Language.objects.all()

        if self.q:
            qs = qs.filter(name_native__icontains=self.q)

        return qs

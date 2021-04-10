from django.contrib import admin
from django.forms import ModelForm, CharField
from ckeditor.widgets import CKEditorWidget

from .models import Institution, RefNumber, Author, SourceType, Document, User


class InstitutionAdmin(admin.ModelAdmin):
    """Admin model for the institutions. """

    list_display = ('institution_name', 'street', 'zip_code', 'city', 'country', 'site_url', 'institution_slug')
    prepopulated_fields = {'institution_slug': ('institution_name',)}


class RefNumberAdmin(admin.ModelAdmin):
    """Admin model for the reference numbers. """

    list_display = ('ref_number_name', 'ref_number_title', 'holding_institution', 'ref_number_slug')
    prepopulated_fields = {'ref_number_slug': ('ref_number_name',)}


class DocumentAdminForm(ModelForm):
    """Overwrites the Admin form for the Document object to use the ckEditor as widget for the transcription."""

    transcription_text = CharField(widget=CKEditorWidget())

    class Meta:
        model = Document
        fields = '__all__'


class DocumentAdmin(admin.ModelAdmin):
    """Admin model for the Documents. """

    form = DocumentAdminForm

    list_display = ('title_name', 'parent_institution', 'parent_ref_number', 'document_slug')
    prepopulated_fields = {'document_slug': ('title_name',)}
    readonly_fields = ('submitted_by', 'document_utc_add')

    def save_model(self, request, obj: Document, form, change):
        if not obj.pk:
            # If generated in the admin, use the currently logged in user as submitter
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(active=True)


class SourceTypeAdmin(admin.ModelAdmin):
    """Admin model for the source types. """

    list_display = ('type_name', 'parent_type')


admin.site.register(Institution, InstitutionAdmin)
admin.site.register(RefNumber, RefNumberAdmin)
admin.site.register(Author)
admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(User)

from django.contrib import admin
from .models import Institution, RefNumber, Author, SourceLanguage, SourceType, DocumentTitle, User


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('institution_name', 'street', 'zip_code', 'city', 'country', 'site_url', 'institution_slug')
    prepopulated_fields = {'institution_slug': ('institution_name',)}


class RefNumberAdmin(admin.ModelAdmin):
    list_display = ('refnumber_name', 'refnumber_title', 'holding_institution', 'refnumber_slug')
    prepopulated_fields = {'refnumber_slug': ('refnumber_name',)}


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title_name', 'parent_institution', 'parent_refnumber', 'document_slug')
    prepopulated_fields = {'document_slug': ('title_name',)}
    readonly_fields = ('submitted_by', 'document_utc_add')

    def save_model(self, request, obj: DocumentTitle, form, change):
        if not obj.pk:
            # If generated in the admin, use the currently logged in user as submitter
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(active=True)

class SourceTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'parent_type')

admin.site.register(Institution, InstitutionAdmin)
admin.site.register(RefNumber, RefNumberAdmin)
admin.site.register(Author)
admin.site.register(SourceLanguage)
admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(DocumentTitle, DocumentAdmin)
admin.site.register(User)

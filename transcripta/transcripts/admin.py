from django.contrib import admin
from .models import Institution, RefNumber, Author, SourceLanguage, SourceType, DocumentTitle, User

# Register your models here.

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('institution_name', 'street', 'zip_code', 'city', 'country', 'site_url', 'institution_slug')
    prepopulated_fields = {'institution_slug': ('institution_name',)}

class RefNumberAdmin(admin.ModelAdmin):
    list_display = ('refnumber_name', 'refnumber_title', 'holding_institution', 'refnumber_slug')
    prepopulated_fields = {'refnumber_slug': ('refnumber_name',)}

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title_name', 'parent_institution', 'parent_refnumber', 'document_slug')
    prepopulated_fields = {'document_slug': ('title_name',)}

admin.site.register(Institution, InstitutionAdmin)
admin.site.register(RefNumber, RefNumberAdmin)
admin.site.register(Author)
admin.site.register(SourceLanguage)
admin.site.register(SourceType)
admin.site.register(DocumentTitle, DocumentAdmin)
admin.site.register(User)
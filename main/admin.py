from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import ModelForm, CharField
from ckeditor.widgets import CKEditorWidget
from easy_select2 import select2_modelform
from .models import Institution, RefNumber, Author, SourceType, Document, User, UserSubscription

InstitutionForm = select2_modelform(Institution, attrs={'width': '250px'})


class InstitutionAdmin(admin.ModelAdmin):
    """Admin model for the institutions. """
    list_display = ('institution_name', 'street', 'zip_code', 'city', 'country', 'site_url', 'institution_slug')
    prepopulated_fields = {'institution_slug': ('institution_name',)}
    # form = InstitutionForm


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


class ActiveDocumentListFilter(admin.SimpleListFilter):
    title = 'Only show latest versions of documents'
    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return(
            ('latest', 'Show latest versions only'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'latest':
            return queryset.filter(active=True)


class DocumentAdmin(admin.ModelAdmin):
    """Admin model for the Documents. """

    form = DocumentAdminForm

    list_display = ('title_name', 'institution_name', 'parent_ref_number', 'version_number', 'document_utc_add')
    list_filter = (ActiveDocumentListFilter,)
    search_fields = ['title_name', 'parent_ref_number__holding_institution__institution_name', 'parent_ref_number__ref_number_name']
    prepopulated_fields = {'document_slug': ('title_name',)}
    readonly_fields = ('submitted_by', 'document_utc_add')
    actions = None

    @admin.display(description='institution')
    def institution_name(self, obj):
        return obj.parent_ref_number.holding_institution.institution_name

    def save_model(self, request, obj: Document, form, change):
        if not obj.pk:
            # If generated in the admin, use the currently logged in user as submitter
            obj.submitted_by = request.user
        obj.save(force_update=True)

    def get_queryset(self, request):
        # use all_objects instead of the default manager
        return self.model.all_objects.get_queryset()


class SourceTypeAdmin(admin.ModelAdmin):
    """Admin model for the source types. """

    list_display = ('type_name', 'parent_type')


class MyUserAdmin(UserAdmin):
    readonly_fields = ('date_joined', )
    list_display = ('username', 'is_superuser')


admin.site.register(Institution, InstitutionAdmin)
admin.site.register(RefNumber, RefNumberAdmin)
admin.site.register(Author)
admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(User, MyUserAdmin)
admin.site.register(UserSubscription)

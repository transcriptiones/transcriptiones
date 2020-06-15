from .displayviews import InstitutionListView, InstitutionDetailView, RefNumberDetailView, DocumentTitleDetailView, DocumentHistoryView
from .infoviews import StartView
from .searchviews import SearchView
from .uploadviews import AddInstitutionView, AddRefNumberView, AddDocumentView, RedirectView, load_refnumbers, EditMetaView, EditTranscriptView, batchupload
from .userviews import signup, AccountActivationSentView, activate, CustomLoginView, CustomPasswordChangeView, userprofile, UserUpdateView, CustomPasswordResetView, CustomPasswordConfirmView

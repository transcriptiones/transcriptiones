from .displayviews import InstitutionListView, InstitutionDetailView, RefNumberDetailView, DocumentTitleDetailView, DocumentHistoryView
from .infoviews import StartView
from .searchviews import SearchView, ResultsView
from .uploadviews import AddInstitutionView, AddRefNumberView, AddDocumentView, RedirectView, load_refnumbers, EditMetaView, EditTranscriptView
from .userviews import signup, AccountActivationSentView, activate, CustomLoginView, CustomPasswordChangeView, userprofile, UserUpdateView, CustomPasswordResetView, CustomPasswordConfirmView

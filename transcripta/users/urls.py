from django.urls import path
from transcripta.users.views import signup, AccountActivationSent, activate

urlpatterns = [
    path('signup', signup, name = "signup"),
    path('activationsent', AccountActivationSent.as_view(), name = "account_activation_sent"),
    path('activate/<uidb64>/<token>', activate, name = "activate"),
    ]
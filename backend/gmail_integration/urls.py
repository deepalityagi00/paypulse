from django.urls import path

from .views import GmailAuthInitView, GmailCallbackView

app_name = "gmail_integration"

urlpatterns = [
    path("auth/", GmailAuthInitView.as_view(), name="auth-init"),
    path("callback/", GmailCallbackView.as_view(), name="auth-callback"),
]

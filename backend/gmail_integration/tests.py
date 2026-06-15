"""Tests for the Gmail OAuth 2.0 class-based views (sign-up / sign-in flow)."""
from datetime import datetime
from unittest import mock

from cryptography.fernet import Fernet
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from gmail_integration.models import GmailCredential
from gmail_integration.utility import TextSecurity
from gmail_integration.views import OAUTH_STATE_SESSION_KEY

User = get_user_model()

# A real Fernet key so TextSecurity can encrypt/decrypt during tests.
TEST_FERNET_KEY = Fernet.generate_key().decode("utf-8")

COMMON_SETTINGS = dict(
    FERNET_KEY=TEST_FERNET_KEY,
    FRONTEND_URL="http://testfrontend.local",
    GMAIL_CLIENT_ID="client-id",
    GMAIL_CLIENT_SECRET="client-secret",
    GMAIL_REDIRECT_URI="http://testserver/gmail/callback/",
    GMAIL_SCOPES="https://www.googleapis.com/auth/gmail.readonly",
)


@override_settings(**COMMON_SETTINGS)
class GmailAuthInitViewTests(TestCase):
    def setUp(self):
        self.url = reverse("gmail_integration:auth-init")

    @mock.patch("gmail_integration.views.build_flow")
    def test_anonymous_user_is_redirected_to_google(self, mock_build_flow):
        flow = mock.Mock()
        flow.authorization_url.return_value = (
            "https://accounts.google.com/o/oauth2/auth?state=xyz",
            "xyz",
        )
        mock_build_flow.return_value = flow

        # No login — this is the sign-up entry point.
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            "https://accounts.google.com/o/oauth2/auth?state=xyz",
        )
        self.assertEqual(self.client.session[OAUTH_STATE_SESSION_KEY], "xyz")

    @mock.patch("gmail_integration.views.build_flow")
    def test_login_hint_is_forwarded(self, mock_build_flow):
        flow = mock.Mock()
        flow.authorization_url.return_value = ("https://accounts.google.com/x", "s")
        mock_build_flow.return_value = flow

        self.client.get(self.url, {"login_hint": "alice@example.com"})

        _, kwargs = flow.authorization_url.call_args
        self.assertEqual(kwargs["login_hint"], "alice@example.com")


@override_settings(**COMMON_SETTINGS)
class GmailCallbackViewTests(TestCase):
    def setUp(self):
        self.url = reverse("gmail_integration:auth-callback")

    def _set_state(self, state):
        session = self.client.session
        session[OAUTH_STATE_SESSION_KEY] = state
        session.save()

    def _mock_credentials(self):
        creds = mock.Mock()
        creds.token = "access-token-123"
        creds.refresh_token = "refresh-token-456"
        creds.expiry = datetime(2030, 1, 1, 0, 0, 0)  # naive UTC
        creds.scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
        return creds

    @mock.patch("gmail_integration.views.get_profile_email")
    @mock.patch("gmail_integration.views.build_flow")
    def test_first_time_signin_creates_user_logs_in_and_stores_tokens(
        self, mock_build_flow, mock_get_email
    ):
        creds = self._mock_credentials()
        flow = mock.Mock()
        flow.credentials = creds
        mock_build_flow.return_value = flow
        mock_get_email.return_value = "bob.gmail@example.com"

        self._set_state("good-state")
        response = self.client.get(
            self.url, {"code": "auth-code", "state": "good-state"}
        )

        # Redirects back to the SPA with a success flag.
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response["Location"].startswith("http://testfrontend.local/signin")
        )
        self.assertIn("gmail=connected", response["Location"])
        flow.fetch_token.assert_called_once_with(code="auth-code")

        # A user was created from the Google email and logged in.
        user = User.objects.get(email="bob.gmail@example.com")
        self.assertFalse(user.has_usable_password())
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

        # Tokens are stored encrypted but decrypt back to the originals.
        credential = GmailCredential.objects.get(user=user)
        cipher = TextSecurity()
        self.assertNotEqual(credential.encrypted_access_token, "access-token-123")
        self.assertEqual(
            cipher.decrypt(credential.encrypted_access_token).decode("utf-8"),
            "access-token-123",
        )
        self.assertEqual(
            cipher.decrypt(credential.encrypted_refresh_token).decode("utf-8"),
            "refresh-token-456",
        )
        self.assertIsNotNone(credential.token_expiry.tzinfo)
        self.assertNotIn(OAUTH_STATE_SESSION_KEY, self.client.session)

    @mock.patch("gmail_integration.views.get_profile_email")
    @mock.patch("gmail_integration.views.build_flow")
    def test_returning_user_is_reused_and_credential_updated(
        self, mock_build_flow, mock_get_email
    ):
        existing = User.objects.create_user(
            username="bob.gmail@example.com",
            email="bob.gmail@example.com",
            password="pw12345!",
        )
        GmailCredential.objects.create(
            user=existing,
            name="old",
            email="bob.gmail@example.com",
            encrypted_access_token="x",
            encrypted_refresh_token="y",
            scopes=[],
        )

        creds = self._mock_credentials()
        flow = mock.Mock()
        flow.credentials = creds
        mock_build_flow.return_value = flow
        mock_get_email.return_value = "bob.gmail@example.com"

        self._set_state("good-state")
        response = self.client.get(
            self.url, {"code": "auth-code", "state": "good-state"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("gmail=connected", response["Location"])
        # No duplicate user or credential created.
        self.assertEqual(User.objects.filter(email="bob.gmail@example.com").count(), 1)
        self.assertEqual(GmailCredential.objects.filter(user=existing).count(), 1)
        credential = GmailCredential.objects.get(user=existing)
        self.assertEqual(
            TextSecurity().decrypt(credential.encrypted_access_token).decode("utf-8"),
            "access-token-123",
        )

    def test_callback_redirects_with_error_on_invalid_state(self):
        self._set_state("expected-state")
        response = self.client.get(self.url, {"code": "auth-code", "state": "wrong"})

        self.assertEqual(response.status_code, 302)
        self.assertIn("gmail=error", response["Location"])
        self.assertIn("reason=invalid_state", response["Location"])
        self.assertFalse(GmailCredential.objects.exists())
        self.assertFalse(User.objects.exists())

    def test_callback_redirects_with_error_when_code_missing(self):
        self._set_state("expected-state")
        response = self.client.get(self.url, {"state": "expected-state"})

        self.assertEqual(response.status_code, 302)
        self.assertIn("reason=missing_code", response["Location"])

    def test_callback_redirects_with_error_on_provider_error(self):
        self._set_state("expected-state")
        response = self.client.get(
            self.url, {"error": "access_denied", "state": "expected-state"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("gmail=error", response["Location"])
        self.assertIn("reason=access_denied", response["Location"])
        self.assertFalse(User.objects.exists())

    @mock.patch("gmail_integration.views.build_flow")
    def test_callback_redirects_with_error_on_token_exchange_failure(
        self, mock_build_flow
    ):
        flow = mock.Mock()
        flow.fetch_token.side_effect = ValueError("bad code")
        mock_build_flow.return_value = flow

        self._set_state("good-state")
        response = self.client.get(
            self.url, {"code": "auth-code", "state": "good-state"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("reason=exchange_failed", response["Location"])
        self.assertFalse(GmailCredential.objects.exists())
        self.assertFalse(User.objects.exists())

"""Tests for the Gmail OAuth 2.0 class-based views."""
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


@override_settings(
    FERNET_KEY=TEST_FERNET_KEY,
    GMAIL_CLIENT_ID="client-id",
    GMAIL_CLIENT_SECRET="client-secret",
    GMAIL_REDIRECT_URI="https://testserver/gmail/callback/",
    GMAIL_SCOPES="https://www.googleapis.com/auth/gmail.readonly",
)
class GmailAuthInitViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice", email="alice@example.com", password="pw12345!"
        )
        self.url = reverse("gmail_integration:auth-init")

    def test_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @mock.patch("gmail_integration.views.build_flow")
    def test_redirects_to_google_and_stores_state(self, mock_build_flow):
        flow = mock.Mock()
        flow.authorization_url.return_value = (
            "https://accounts.google.com/o/oauth2/auth?state=xyz",
            "xyz",
        )
        mock_build_flow.return_value = flow
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            "https://accounts.google.com/o/oauth2/auth?state=xyz",
        )
        self.assertEqual(self.client.session[OAUTH_STATE_SESSION_KEY], "xyz")
        flow.authorization_url.assert_called_once_with(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )


@override_settings(
    FERNET_KEY=TEST_FERNET_KEY,
    GMAIL_CLIENT_ID="client-id",
    GMAIL_CLIENT_SECRET="client-secret",
    GMAIL_REDIRECT_URI="https://testserver/gmail/callback/",
    GMAIL_SCOPES="https://www.googleapis.com/auth/gmail.readonly",
)
class GmailCallbackViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="bob", email="bob@example.com", password="pw12345!"
        )
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

    def test_requires_authentication(self):
        response = self.client.get(self.url, {"code": "abc", "state": "s"})
        self.assertEqual(response.status_code, 403)

    @mock.patch("gmail_integration.views.get_profile_email")
    @mock.patch("gmail_integration.views.build_flow")
    def test_successful_callback_stores_encrypted_tokens(
        self, mock_build_flow, mock_get_email
    ):
        creds = self._mock_credentials()
        flow = mock.Mock()
        flow.credentials = creds
        mock_build_flow.return_value = flow
        mock_get_email.return_value = "bob.gmail@example.com"

        self.client.force_login(self.user)
        self._set_state("good-state")

        response = self.client.get(self.url, {"code": "auth-code", "state": "good-state"})

        self.assertEqual(response.status_code, 200)
        flow.fetch_token.assert_called_once_with(code="auth-code")

        credential = GmailCredential.objects.get(user=self.user)
        self.assertEqual(credential.email, "bob.gmail@example.com")
        self.assertEqual(credential.status, GmailCredential.CredentialStatus.ACTIVE)
        self.assertEqual(
            credential.scopes, ["https://www.googleapis.com/auth/gmail.readonly"]
        )

        # Tokens are stored encrypted, not in plaintext, but decrypt round-trips.
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

        # Expiry was made timezone-aware.
        self.assertIsNotNone(credential.token_expiry.tzinfo)
        # State is cleared from the session after use.
        self.assertNotIn(OAUTH_STATE_SESSION_KEY, self.client.session)

    @mock.patch("gmail_integration.views.get_profile_email")
    @mock.patch("gmail_integration.views.build_flow")
    def test_callback_updates_existing_credential(self, mock_build_flow, mock_get_email):
        GmailCredential.objects.create(
            user=self.user,
            name="old",
            email="old@example.com",
            encrypted_access_token="x",
            encrypted_refresh_token="y",
            scopes=[],
        )
        creds = self._mock_credentials()
        flow = mock.Mock()
        flow.credentials = creds
        mock_build_flow.return_value = flow
        mock_get_email.return_value = "bob.gmail@example.com"

        self.client.force_login(self.user)
        self._set_state("good-state")

        response = self.client.get(self.url, {"code": "auth-code", "state": "good-state"})

        self.assertEqual(response.status_code, 200)
        # Still only one credential (OneToOne) — it was updated in place.
        self.assertEqual(GmailCredential.objects.filter(user=self.user).count(), 1)
        credential = GmailCredential.objects.get(user=self.user)
        self.assertEqual(credential.email, "bob.gmail@example.com")

    def test_callback_rejects_invalid_state(self):
        self.client.force_login(self.user)
        self._set_state("expected-state")

        response = self.client.get(self.url, {"code": "auth-code", "state": "wrong"})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(GmailCredential.objects.exists())

    def test_callback_requires_code(self):
        self.client.force_login(self.user)
        self._set_state("expected-state")

        response = self.client.get(self.url, {"state": "expected-state"})

        self.assertEqual(response.status_code, 400)

    def test_callback_handles_provider_error(self):
        self.client.force_login(self.user)
        self._set_state("expected-state")

        response = self.client.get(
            self.url, {"error": "access_denied", "state": "expected-state"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(GmailCredential.objects.exists())

    @mock.patch("gmail_integration.views.build_flow")
    def test_callback_handles_token_exchange_failure(self, mock_build_flow):
        flow = mock.Mock()
        flow.fetch_token.side_effect = ValueError("bad code")
        mock_build_flow.return_value = flow

        self.client.force_login(self.user)
        self._set_state("good-state")

        response = self.client.get(self.url, {"code": "auth-code", "state": "good-state"})

        self.assertEqual(response.status_code, 502)
        self.assertFalse(GmailCredential.objects.exists())

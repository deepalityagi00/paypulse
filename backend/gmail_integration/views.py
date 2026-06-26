from __future__ import annotations

import logging
from datetime import timezone as dt_timezone
from urllib.parse import urlencode

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect

from .models import GmailCredential
from .oauth import build_flow, get_profile_email
from .utility import TextSecurity

logger = logging.getLogger(__name__)

User = get_user_model()

# Session key under which the OAuth state is stashed between the init and
# callback requests for CSRF protection.
OAUTH_STATE_SESSION_KEY = "gmail_oauth_state"
OAUTH_CODE_VERIFIER ="oauth_code_verifier"

def _frontend_redirect(**params):
    """Redirect to the SPA's sign-in page, carrying a status in the query."""
    base = settings.FRONTEND_URL.rstrip("/") + "/signin"
    query = urlencode(params)
    return redirect(f"{base}?{query}" if query else base)


class GmailAuthInitView(APIView):
    """Start the Gmail OAuth flow by redirecting to Google's consent screen.

    This is the app's sign-up / sign-in entry point, so it is intentionally
    public — the user is not authenticated yet; signing in with Google is how
    they authenticate.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        flow = build_flow()
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            # Pre-select the account the user typed in the sign-in popup.
            login_hint=request.query_params.get("login_hint", ""),
        )
        request.session[OAUTH_STATE_SESSION_KEY] = state
        request.session[OAUTH_CODE_VERIFIER] = flow.code_verifier
        return redirect(authorization_url)


class GmailCallbackView(APIView):
    """Handle Google's redirect: exchange the code, sign the user in, store tokens.

    Public for the same reason as the init view — Google redirects the browser
    here before any Django session user exists. We resolve (or create) the user
    from their verified Google email, log them in, then persist the tokens.
    """

    permission_classes = [AllowAny]

    @staticmethod
    def _get_or_create_user(email):
        """Find the user for this Google email, creating one on first sign-in."""
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email},
        )
        if created:
            # OAuth users have no usable Django password — they log in via Google.
            user.set_unusable_password()
            user.save(update_fields=["password"])
        return user

    @staticmethod
    def _store_credentials(user, credentials, email):
        """Encrypt and persist the OAuth tokens for ``user``."""
        cipher = TextSecurity()

        expiry = credentials.expiry
        if expiry is not None and expiry.tzinfo is None:
            # google-auth returns a naive UTC datetime; make it aware.
            expiry = expiry.replace(tzinfo=dt_timezone.utc)

        credential, _ = GmailCredential.objects.update_or_create(
            user=user,
            defaults={
                "name": email or user.get_username(),
                "email": email,
                "status": GmailCredential.CredentialStatus.ACTIVE,
                "encrypted_access_token": cipher.encrypt(credentials.token or ""),
                "encrypted_refresh_token": cipher.encrypt(
                    credentials.refresh_token or ""
                ),
                "token_expiry": expiry,
                "scopes": list(credentials.scopes or []),
            },
        )
        # TODO Add the Audit trail
        return credential

    def get(self, request):
        # The user denied consent or Google returned an error.
        error = request.query_params.get("error")
        if error:
            return _frontend_redirect(gmail="error", reason=error)

        code = request.query_params.get("code")
        if not code:
            return _frontend_redirect(gmail="error", reason="missing_code")

        # Validate the state parameter against what we stored at init time.
        expected_state = request.session.get(OAUTH_STATE_SESSION_KEY)
        returned_state = request.query_params.get("state")
        if not expected_state or expected_state != returned_state:
            return _frontend_redirect(gmail="error", reason="invalid_state")

        try:
            code_verifier = request.session.get(OAUTH_CODE_VERIFIER)
            flow = build_flow(state=expected_state)
            flow.code_verifier = code_verifier
            flow.fetch_token(code=code)
            credentials = flow.credentials
            email = get_profile_email(credentials)
        except Exception:  # noqa: BLE001 - surface a clean error to the user
            logger.exception("Gmail token exchange failed")
            return _frontend_redirect(gmail="error", reason="exchange_failed")
        finally:
            request.session.pop(OAUTH_STATE_SESSION_KEY, None)

        if not email:
            return _frontend_redirect(gmail="error", reason="no_email")

        # Sign the user in (creating their account on first connect) and store
        # the tokens against them, then hand back to the SPA.
        user = self._get_or_create_user(email)
        login(request, user)
        self._store_credentials(user, credentials, email)

        return _frontend_redirect(gmail="connected", email=email)

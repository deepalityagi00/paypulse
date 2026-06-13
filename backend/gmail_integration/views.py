from __future__ import annotations

import logging
from datetime import timezone as dt_timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import redirect

from .models import GmailCredential
from .oauth import build_flow, get_profile_email
from .utility import TextSecurity

logger = logging.getLogger(__name__)

# Session key under which the OAuth ``state`` is stashed between the init and
# callback requests for CSRF protection.
OAUTH_STATE_SESSION_KEY = "gmail_oauth_state"


class GmailAuthInitView(APIView):
    """Start the Gmail OAuth flow by redirecting to Google's consent screen."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        flow = build_flow()
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        request.session[OAUTH_STATE_SESSION_KEY] = state
        return redirect(authorization_url)


class GmailCallbackView(APIView):
    """Handle Google's redirect: exchange the code and persist the tokens."""

    permission_classes = [IsAuthenticated]


    @staticmethod
    def _store_credentials(user, credentials, email):
        """Encrypt and persist the OAuth tokens for ``user``."""
        cipher = TextSecurity()

        expiry = credentials.expiry
        if expiry is not None and expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=dt_timezone.utc)

        access_token = cipher.encrypt(credentials.token or "")
        refresh_token = cipher.encrypt(credentials.refresh_token or "")

        credential, _ = GmailCredential.objects.update_or_create(
            user=user,
            defaults={
                "name": email or user.get_username(),
                "email": email,
                "status": GmailCredential.CredentialStatus.ACTIVE,
                "encrypted_access_token": access_token,
                "encrypted_refresh_token": refresh_token,
                "token_expiry": expiry,
                "scopes": list(credentials.scopes or []),
            },
        )
        #TODO Add the Audit trail
        return credential

    def get(self, request):
        # The user denied consent or Google returned an error.
        error = request.query_params.get("error")
        if error:
            return Response(
                {"detail": f"Authorization failed: {error}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        code = request.query_params.get("code")
        if not code:
            return Response(
                {"detail": "Missing authorization code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate the state parameter against what we stored at init time.
        expected_state = request.session.get(OAUTH_STATE_SESSION_KEY)
        returned_state = request.query_params.get("state")
        if expected_state != returned_state:
            return Response(
                {"detail": "Invalid OAuth state."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            flow = build_flow(state=expected_state)
            flow.fetch_token(code=code)
            credentials = flow.credentials
            email = get_profile_email(credentials)
        except Exception:  # noqa: BLE001 - surface a clean error to the client
            logger.exception("Gmail token exchange failed for user %s", request.user.pk)
            return Response(
                {"detail": "Failed to complete Gmail authorization."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        finally:
            request.session.pop(OAUTH_STATE_SESSION_KEY, None)

        credential = self._store_credentials(request.user, credentials, email)

        return Response(
            {
                "detail": "Gmail account connected successfully.",
                "id": str(credential.id),
                "email": credential.email,
                "scopes": credential.scopes,
                "status": credential.status,
            },
            status=status.HTTP_200_OK,
        )

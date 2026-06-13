"""Helpers for the Gmail OAuth 2.0 authorization flow.

Centralises construction of the ``google-auth-oauthlib`` Flow and the small
amount of Google API access we need so the views stay thin and the flow can be
mocked easily in tests.
"""
from __future__ import annotations

import re

from django.conf import settings
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


def get_gmail_scopes():
    """Return the configured Gmail scopes as a list.
    """
    return [scope.strip() for scope in settings.GMAIL_SCOPES.split(',') if scope.strip()]


def _client_config():
    """Build the client config dict expected by ``Flow.from_client_config``."""
    return {
        "web": {
            "client_id": settings.GMAIL_CLIENT_ID,
            "client_secret": settings.GMAIL_CLIENT_SECRET,
            "auth_uri": settings.GMAIL_AUTH_URL,
            "token_uri": settings.GMAIL_TOKEN_URL,
            "redirect_uris": [settings.GMAIL_REDIRECT_URI],
        }
    }


def build_flow(state=None):
    """Return a configured OAuth :class:`Flow` for the Gmail authorization."""
    flow = Flow.from_client_config(
        _client_config(),
        scopes=get_gmail_scopes(),
        state=state,
    )
    flow.redirect_uri = settings.GMAIL_REDIRECT_URI
    return flow


def get_profile_email(credentials):
    """Fetch the connected account's email address using the Gmail profile API."""
    service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
    profile = service.users().getProfile(userId="me").execute()
    return profile.get("emailAddress")

from uuid import uuid4
from django.conf import settings
from django.db import models


class GmailCredential(models.Model):
    """Stores OAuth 2.0 tokens for a user's Gmail account."""
    class CredentialStatus(models.TextChoices):
        ACTIVE = ("active", "Active")
        REVOKED = ("revoked", "Revoked")
        DISCONNECTED = ("disconnected", "Disconnected")
        EXPIRED = ("expired", "Expired")
        
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    #TODO V2 Multiple-Inbox support for a user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gmail_cred",
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True)
    status = models.CharField(max_length=20,choices=CredentialStatus.choices, default=CredentialStatus.ACTIVE)
    encrypted_access_token = models.TextField()
    encrypted_refresh_token = models.TextField()
    token_expiry = models.DateTimeField(null=True, blank=True)
    # Stores the authorized scopes 
    scopes = models.JSONField(default=list)
    # Track the last read Emails 
    last_history_id = models.CharField(max_length=64, blank=True,default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GmailCredential for {self.user}"

    class Meta:
        db_table="gmail_credentials"
        ordering = ["-created_at"]

class SyncLog(models.Model):
    """Records each Gmail sync attempt for a user."""

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILURE = "failure", "Failure"

    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    # useful for v2, for multiple-inbox, we can have sync for specific gmails
    gmail_connection = models.ForeignKey(
        GmailCredential,
        on_delete=models.CASCADE,
        related_name="sync_logs",
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.SUCCESS
    )
    messages_synced = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    synced_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "synclog"
        ordering = ["-synced_at"]

    def __str__(self):
        return f"SyncLog({self.gmail_connection}, {self.status}, {self.synced_at:%Y-%m-%d %H:%M})"

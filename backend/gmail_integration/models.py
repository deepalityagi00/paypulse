from django.conf import settings
from django.db import models


class GmailCredential(models.Model):
    """Stores OAuth 2.0 tokens for a user's Gmail account."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gmail_credential",
    )
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expiry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GmailCredential for {self.user}"


class SyncLog(models.Model):
    """Records each Gmail sync attempt for a user."""

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILURE = "failure", "Failure"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
        ordering = ["-synced_at"]

    def __str__(self):
        return f"SyncLog({self.user}, {self.status}, {self.synced_at:%Y-%m-%d %H:%M})"

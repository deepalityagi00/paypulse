from django.conf import settings
from django.db import models


class Invoice(models.Model):
    """Represents a single invoice in the system."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    number = models.CharField(max_length=50)
    recipient_name = models.CharField(max_length=255)
    recipient_email = models.EmailField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.DRAFT
    )
    issue_date = models.DateField()
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invoice {self.number} – {self.recipient_name}"

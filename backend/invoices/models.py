from uuid import uuid4
from django.conf import settings
from django.db import models


class Client(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clients",
    )
    email = models.EmailField()
    name = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.email

    class Meta:
        db_table = "client"
        unique_together = ("user", "email")

class Invoice(models.Model):
    """Represents a single invoice in the system."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"
        VOID = "void", "Void"
        DISPUTED = "disputed", "Disputed"

    class Currency(models.TextChoices):
        USD = "USD", "US Dollar"
        EUR = "EUR", "Euro"
        GBP = "GBP", "British Pound"
        INR = "INR", "Indian Rupee"
        AUD = "AUD", "Australian Dollar"
        CAD = "CAD", "Canadian Dollar"


    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    number = models.CharField(max_length=50)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="received_invoices",
    )
    gmail_message_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    # Stripe invoice id created in the Stripe platform
    stripe_invoice_id = models.CharField(max_length=300, blank=True, null=True)

    # Amount in cents to avoid floating point issues
    amount = models.IntegerField(default=0) 
    gst_amount = models.IntegerField(default=0)
    hst_amount = models.IntegerField(default=0)     
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.CAD)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    issue_date = models.DateField()
    due_date = models.DateField()

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "invoice"
        unique_together = ("owner", "number")
        ordering = ["-created_at"]


    def __str__(self):
        return f"Invoice {self.number} - {self.amount} {self.currency} - {self.status}"

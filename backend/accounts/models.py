from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid import uuid4

class User(AbstractUser):
    """Custom user model for PayPulse."""

    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    class Meta:
        db_table = "users"

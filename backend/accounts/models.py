from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model – extend as needed."""

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

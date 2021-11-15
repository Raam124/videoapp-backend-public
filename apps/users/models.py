from django.utils.translation import gettext_lazy as _
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser

class AccountStatus(models.TextChoices):
    PENDING_EMAIL = 'PENDING_EMAIL', _('PENDING_EMAIL')
    VERIFIED = 'VERIFIED', _('VERIFIED')

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_name = models.CharField(max_length=200, null=True, blank=True, default=None)
    phone = models.CharField(max_length=15, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    account_status = models.CharField(
        max_length=20,
        choices=AccountStatus.choices,
        default=AccountStatus.PENDING_EMAIL
    )

class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='verification')
    token = models.CharField(max_length=25)
    is_valid = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

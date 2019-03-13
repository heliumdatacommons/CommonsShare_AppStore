from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import JSONField

from pivot_orchestration_service.models import ApplianceStatus

# Create your models here.


class TransmartHCMConfig(models.Model):
    """
    i2b2 transmart copdgene configuration model
    """
    data = JSONField()

    def __str__(self):
        return 'i2b2 Transmart HCM Configuration in JSON format'

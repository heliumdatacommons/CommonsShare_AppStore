from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.


class TransmartCOPDGeneConfig(models.Model):
    """
    i2b2 transmart copdgene configuration model
    """
    data = JSONField()

    def __str__(self):
        return 'i2b2 Transmart COPDGene Configuration in JSON format'

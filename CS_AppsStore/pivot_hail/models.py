from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.


class HailConfig(models.Model):
    """
    HAIL configuration model
    """
    data = JSONField()

    def __str__(self):
        return 'HAIL Configuration in JSON format'

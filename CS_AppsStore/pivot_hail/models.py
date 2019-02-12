# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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


class HailStatus(models.Model):
    """
    model to keep track of hail cluster status
    """
    appliance_id = models.CharField(max_length=160)
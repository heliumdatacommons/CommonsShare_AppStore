# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
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
    STATUS = (
        ('R', 'running'),
        ('D', 'deleted'),
    )
    user = models.ForeignKey(User, editable=False, null=False, on_delete=models.CASCADE,
                             related_name='hail_status', related_query_name='hail_status')
    appliance_id = models.CharField(max_length=160)
    status = models.CharField(max_length=2, choices=STATUS, default='R')
    insts = models.PositiveIntegerField()
    # in MB unit
    memory = models.PositiveIntegerField()
    cpus = models.PositiveIntegerField()
    # time the appliance is started or deleted depending on the status
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "appliance_id", "status", "timestamp")

    def __unicode__(self):
        return '{}-{}-{}'.format(self.user.username, self.appliance_id, self.status)

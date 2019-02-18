from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import JSONField

from pivot_orchestration_service.models import ApplianceStatus

# Create your models here.


class HailConfig(models.Model):
    """
    HAIL configuration model
    """
    data = JSONField()

    def __str__(self):
        return 'HAIL Configuration in JSON format'


class HailStatus(ApplianceStatus):
    """
    model to keep track of hail cluster status
    """
    user = models.ForeignKey(User, editable=False, null=False, on_delete=models.CASCADE,
                             related_name='hail_status', related_query_name='hail_status')
    insts = models.PositiveIntegerField()
    # in MB unit
    memory = models.PositiveIntegerField()
    cpus = models.PositiveIntegerField()

    def __unicode__(self):
        return '{}-{}-{}'.format(self.user.username, self.appliance_id, self.status)

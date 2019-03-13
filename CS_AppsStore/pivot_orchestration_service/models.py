from django.db import models

# Create your models here.

from django.contrib.auth.models import User

# Create your models here.


class ApplianceStatus(models.Model):
    """
    model to keep track of hail cluster status
    """
    STATUS = (
        ('R', 'running'),
        ('D', 'deleted'),
    )
    user = models.ForeignKey(User, editable=False, null=False, on_delete=models.CASCADE)
    appliance_id = models.CharField(max_length=160)
    status = models.CharField(max_length=2, choices=STATUS, default='R')

    # the appliance start and end time stamps
    start_timestamp = models.DateTimeField(null=True, blank=True)
    end_timestamp = models.DateTimeField(null=True, blank=True)

    cpus = models.PositiveIntegerField(null=True, blank=True)
    # in MB unit
    memory = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "appliance_id", "status", "start_timestamp", "end_timestamp")

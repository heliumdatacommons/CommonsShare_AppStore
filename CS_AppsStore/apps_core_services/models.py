# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organizations = models.TextField(blank=True, null=True)


class CSApp(models.Model):
    name = models.CharField(max_length=255)
    url = models.TextField()
    logo = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class PivotHailConfig(AppConfig):
    name = 'pivot_hail'
    verbose_name = 'Deploy HAIL Cluster on PIVOT Appliance'
    url = '/pivot_hail/login_start/'
    logo = 'img/pivot_logo.jpg'

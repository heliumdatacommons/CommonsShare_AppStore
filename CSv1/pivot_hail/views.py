# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def deploy(request):
    user = request.user

@login_required
def start(request):
    return render(request, "pivot_hail/start.html", {})

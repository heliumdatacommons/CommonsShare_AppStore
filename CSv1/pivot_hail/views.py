# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import re
from json import load

from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

from models import HailConfig

# Create your views here.

@login_required
def deploy(request):
    conf_qs = HailConfig.objects.all()
    if not conf_qs:
        errmsg = "PIVOT JSON Configuration file cannot be loaded"
        messages.error(request, errmsg)
        if request.is_ajax():
            return JsonResponse(data={'error': errmsg},
                                status=500)
        else:
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

    user = request.user
    # append username to appliance id from JSON request file to make each user to have a
    # unique appliance to work with without stamping over each other
    hashed_user_id = hashlib.sha256(b'' + user.username).hexdigest()[0:10]
    conf_data = conf_qs.first().data
    app_id = conf_data['id'] + hashed_user_id
    conf_data['id'] = app_id

    # validate app_id
    id_validation_failure_msg = 'appliance or container id {} failed validation - id can only ' \
                                'contain dash, underline, letters, and numbers'
    id_re = re.compile('^[a-zA-Z0-9_-]+$')
    if not id_re.match(app_id):
        if request.is_ajax():
            return JsonResponse(data={'error': id_validation_failure_msg.format(app_id)},
                                status=500)
        else:
            return HttpResponseBadRequest(content=id_validation_failure_msg.format(app_id))

    return render(request, "pivot_hail/start.html", {})


@login_required
def start(request):
    conf_qs = HailConfig.objects.all()
    if not conf_qs:
        config_file = 'pivot_hail/data/pivot_hail.json'
        with open(config_file, 'r') as fp:
            p_data = load(fp)
            if not 'id' in p_data or not 'containers' in p_data:
                errmsg = "PIVOT JSON Configuration file is not valid"
                messages.error(request, errmsg)
                if request.is_ajax():
                    return JsonResponse(data={'error': errmsg},
                                        status=500)
                else:
                    return HttpResponseRedirect(request.META['HTTP_REFERER'])
            HailConfig.objects.create(data=p_data)
    else:
        p_data = HailConfig.objects.all().first().data

    # get default value to show on the start page for users to override as needed
    insts = None
    cpus = None
    mems = None
    context = {}
    for con in p_data['containers']:
        if con['id'] == 'workers':
            insts = con['instances']
            cpus = con['resources']['cpus']
            mems = con['resources']['mem']
            context = {
                'num_instances': str(insts),
                'num_cpus': str(cpus),
                'mem_size': str(mems)
            }
            break


    return render(request, "pivot_hail/start.html", context)

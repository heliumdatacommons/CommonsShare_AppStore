# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import re
from json import load, dumps
import requests

from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest

from rest_framework import status

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
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return HttpResponseBadRequest(content=id_validation_failure_msg.format(app_id))

    num_insts = request.POST.get('num_instances', None)
    num_cpus = request.POST.get('num_cpus', None)
    mem_size = request.POST.get('mem_size', None)
    token = request.POST.get('token', None)
    cluster_name = request.POST.get('opt_cloud', '')

    if cluster_name != 'gcp' and cluster_name != 'aws':
        cluster_name = ''

    url = settings.PIVOT_URL

    for con in conf_data['containers']:
        if con['id'] and not id_re.match(con['id']):
            return HttpResponseBadRequest(content=id_validation_failure_msg.format(con['id']))
        if cluster_name:
            con['rack'] = cluster_name
        if con['id'] == 'workers':
            if num_insts:
                con['instances'] = int(num_insts)
            if num_cpus:
                con['resources']['cpus'] = int(num_cpus)
            if mem_size:
                con['resources']['mem'] = int(mem_size)
        if con['id'] == 'master':
            if token:
                con['env']['JUPYTER_TOKEN'] = token

    app_url = url + '/' + app_id
    get_response = requests.get(app_url)
    if get_response.status_code == status.HTTP_404_NOT_FOUND:
        response = requests.post(url, data=dumps(conf_data))
        if response.status_code != status.HTTP_200_OK and \
                        response.status_code != status.HTTP_201_CREATED:
            if request.is_ajax():
                return JsonResponse(data={'error': response.text},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return HttpResponseBadRequest(content=response.text)

    redirect_url = app_url + '/ui'

    return HttpResponseRedirect(redirect_url)


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
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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

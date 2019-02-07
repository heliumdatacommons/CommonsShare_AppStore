# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import re
from json import load, dumps, loads
import requests
import time

from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse

from rest_framework import status

from models import HailConfig

# Create your views here.

@login_required
def deploy(request):
    conf_qs = HailConfig.objects.all()
    if not conf_qs:
        errmsg = "PIVOT JSON Configuration file cannot be loaded"
        messages.error(request, errmsg)
        return JsonResponse(data={'error': errmsg},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        return JsonResponse(data={'error': id_validation_failure_msg.format(app_id)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    num_insts = request.POST.get('num_instances', None)
    num_cpus = request.POST.get('num_cpus', None)
    mem_size = request.POST.get('mem_size', None)
    token = request.POST.get('token', None)
    cluster_name = request.POST.get('opt_cloud', '')

    if cluster_name != 'gcp' and cluster_name != 'aws':
        cluster_name = ''

    for con in conf_data['containers']:
        if con['id'] and not id_re.match(con['id']):
            return JsonResponse(data={'error': id_validation_failure_msg.format(con['id'])},
                                status=status.HTTP_400_BAD_REQUEST)

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

    # check if appliance already exists, if yes, do redirect directly, if not, create a new one
    url = settings.PIVOT_URL + 'appliance'
    app_url = url + '/' + app_id
    get_response = requests.get(app_url)
    if get_response.status_code == status.HTTP_404_NOT_FOUND:
        # check whether there are enough resources available to create requested HAIL cluster
        response = requests.get(settings.PIVOT_URL + 'cluster')
        return_data = loads(response.content)
        avail_cpus = 0
        avail_mems = 0
        for cluster in return_data:
            avail_cpus += cluster['resources']['cpus']
            avail_mems += cluster['resources']['mem']

        if avail_cpus < 1 or avail_mems < 1000:
            return JsonResponse(data={'error': 'There are no resource available at the moment.'
                                               'Please check <a href="https://github.com/heliump'
                                               'lusdatastage/Reservations/issues/1">HAIL cluster '
                                               'reservation queue</a> to see who are currently '
                                               'using HAIL cluster'},
                                status=status.HTTP_400_BAD_REQUEST)

        req_cpus = settings.INITIAL_COST_CPU + int(num_cpus) * int(num_insts)
        req_mem = settings.INITIAL_COST_MEM + int(mem_size) * int(num_insts)


        if req_cpus <= avail_cpus and req_mem <= avail_mems:
            # there are enough resources, go ahead to request to create HAIL cluster
            response = requests.post(url, data=dumps(conf_data))
            if response.status_code == status.HTTP_409_CONFLICT:
                time.sleep(2)
                response = requests.post(url, data=dumps(conf_data))

            if response.status_code != status.HTTP_200_OK and \
                            response.status_code != status.HTTP_201_CREATED:
                return JsonResponse(data={'error': response.text},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            err_msg = 'There are not enough resources available. Please reduce number of ' \
                      'instances and resources requested to be within our available resource pool ' \
                      '({} CPUs and {}MB memory available at the moment).'
            # there are not enough resources, notify users to reduce number of requested resources
            a_cpus = int(avail_cpus)
            a_mems = int(avail_mems)
            return JsonResponse(data={'error': err_msg.format(a_cpus, a_mems)},
                                status=status.HTTP_400_BAD_REQUEST)

    redirect_url = app_url + '/ui'

    return JsonResponse(status=status.HTTP_200_OK, data={'url': redirect_url})


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
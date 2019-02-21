import hashlib

from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseServerError
from django.utils import timezone
from django.core.exceptions import ValidationError

from rest_framework.status import HTTP_409_CONFLICT, HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, \
    HTTP_400_BAD_REQUEST

from pivot_hail.models import HailConfig, HailStatus
from pivot_hail.utils import get_hail_start_context
from apps_core_services.utils import check_authorization
from pivot_orchestration_service.utils import validate_id, \
    get_running_appliances_usage_status, deploy_appliance, PIVOTException, PIVOTResourceException


# Create your views here.

@login_required
def deploy(request):
    conf_qs = HailConfig.objects.all()
    if not conf_qs:
        errmsg = "PIVOT JSON Configuration file cannot be loaded"
        messages.error(request, errmsg)
        return JsonResponse(data={'error': errmsg},
                            status=HTTP_500_INTERNAL_SERVER_ERROR)

    user = request.user
    # append username to appliance id from JSON request file to make each user to have a
    # unique appliance to work with without stamping over each other
    hashed_user_id = hashlib.sha256(user.username.encode('utf-8')).hexdigest()[0:10]
    conf_data = conf_qs.first().data
    app_id = conf_data['id'] + hashed_user_id
    conf_data['id'] = app_id

    # validate app_id
    try:
        validate_id(app_id)
    except ValidationError as ex:
        return JsonResponse(data={'error': ex.message},
                            status=HTTP_500_INTERNAL_SERVER_ERROR)

    num_insts = request.POST.get('num_instances', None)
    num_cpus = request.POST.get('num_cpus', None)
    mem_size = request.POST.get('mem_size', None)
    token = request.POST.get('token', None)
    cluster_name = request.POST.get('opt_cloud', '')

    if cluster_name != 'gcp' and cluster_name != 'aws':
        cluster_name = ''

    for con in conf_data['containers']:
        if con['id']:
            try:
                validate_id(con['id'])
            except ValidationError as ex:
                return JsonResponse(data={'error': ex.message},
                                    status=HTTP_500_INTERNAL_SERVER_ERROR)

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

    try:
        redirect_url = deploy_appliance(conf_data, check_res_avail=True)
        # new appliance has been created successfully, record new entry into hail cluster
        # status table and make sure status of the existing running appliance get updated from
        # running to deleted
        curr_time = timezone.now()
        HailStatus.objects.filter(user=user, appliance_id=app_id, status='R'). \
            update(status='D', end_timestamp=curr_time)
        HailStatus.objects.create(user=user, appliance_id=app_id, status='R',
                                  insts=num_insts, memory=mem_size, cpus=num_cpus,
                                  start_timestamp=curr_time)
        return JsonResponse(status=HTTP_200_OK, data={'url': redirect_url})

    except PIVOTResourceException as ex:
        err_msg = ex.message + 'Please check <a href="/pivot_hail/status/">HAIL cluster current ' \
                              'usage status</a> to see who are currently using HAIL cluster.'
        return JsonResponse(data={'error': err_msg},
                            status=HTTP_400_BAD_REQUEST)

    except PIVOTException as ex:
        return JsonResponse(data={'error': ex.message},
                            status=HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
def login_start(request):
    # view function when the start action is triggered from CommonsShare Apps Store from
    # which the user has already logged in to CommonsShare Apps Store directly
    context = get_hail_start_context(request)
    if 'error' in context:
        messages.error(request, context['error'])
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    # get default value to show on the start page for users to override as needed
    return render(request, "pivot_hail/start.html", context)


def start(request):
    # view function when the start action is triggered from CommonsShare
    auth_resp = check_authorization(request)
    if auth_resp.status_code != 200:
        return HttpResponseRedirect("/")
    else:
        # this is needed to strip out access token from URL
        return HttpResponseRedirect("/pivot_hail/login_start/")


@login_required()
def status(request):
    url = settings.PIVOT_URL + 'appliance/'
    try:
        context = get_running_appliances_usage_status('pivot_hail.models', 'HailStatus',
                                                      request_url=url)
        return render(request, "pivot_hail/status.html", context)
    except (ImportError, ValidationError) as ex:
        return HttpResponseServerError(ex.message)

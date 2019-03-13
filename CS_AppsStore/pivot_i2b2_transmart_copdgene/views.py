import hashlib
from json import load

from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import ValidationError
from django.utils import timezone

from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST

from pivot_i2b2_transmart_copdgene.models import TransmartCOPDGeneConfig
from apps_core_services.utils import check_authorization
from pivot_orchestration_service.models import ApplianceStatus
from pivot_orchestration_service.utils import validate_id, \
    deploy_appliance, PIVOTException, PIVOTResourceException

# Create your views here.


@login_required
def deploy(request):
    # view function when the deploy action is triggered from CommonsShare Apps Store from
    # which the user has already logged in to CommonsShare Apps Store directly
    conf_qs = TransmartCOPDGeneConfig.objects.all()
    if not conf_qs:
        config_file = 'pivot_i2b2_transmart_copdgene/data/pivot_copdgene.json'
        with open(config_file, 'r') as fp:
            conf_data = load(fp)
            if not 'id' in conf_data or not 'containers' in conf_data:
                errmsg = "PIVOT JSON Configuration file is not valid"
                messages.error(request, errmsg)
                return JsonResponse(data={'error': errmsg},
                                    status=HTTP_500_INTERNAL_SERVER_ERROR)
            TransmartCOPDGeneConfig.objects.create(data=conf_data)
    else:
        conf_data = conf_qs.first().data

    user = request.user
    # append username to appliance id from JSON request file to make each user to have a
    # unique appliance to work with without stamping over each other
    hashed_user_id = hashlib.sha256(user.username.encode('utf-8')).hexdigest()[0:10]
    app_id = conf_data['id'] + hashed_user_id
    conf_data['id'] = app_id

    # validate app_id
    try:
        validate_id(app_id)
    except ValidationError as ex:
        return JsonResponse(data={'error': ex.message},
                            status=HTTP_500_INTERNAL_SERVER_ERROR)

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

    try:
        redirect_url, total_req_cpus, total_req_mem = deploy_appliance(conf_data)
        if total_req_mem > 0 and total_req_mem > 0:
            # new appliance has been created successfully, record new entry into
            # status table and make sure status of the existing running appliance get updated from
            # running to deleted
            curr_time = timezone.now()
            old_appl = ApplianceStatus.objects.filter(user=user, appliance_id=app_id, status='R')
            if old_appl:
                old_appl.update(status='D', end_timestamp=curr_time)
            ApplianceStatus.objects.create(user=user, appliance_id=app_id, status='R',
                                           memory=total_req_mem, cpus=total_req_cpus,
                                           start_timestamp=curr_time)
        return JsonResponse(status=HTTP_200_OK, data={'url': redirect_url})

    except PIVOTResourceException as ex:
        err_msg = ex.message + 'Please check <a href="/pivot/status/">' \
                               'PIVOT cluster current usage status</a> to see who are currently ' \
                               'using the PIVOT cluster.'
        return JsonResponse(data={'error': err_msg},
                            status=HTTP_400_BAD_REQUEST)

    except PIVOTException as ex:
        return JsonResponse(data={'error': str(ex.message)},
                            status=HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
def login_start(request):
    # view function when the start action is triggered from CommonsShare Apps Store from
    # which the user has already logged in to CommonsShare Apps Store directly
    return render(request, "pivot_i2b2_transmart_copdgene/start.html", {})


def start(request):
    # view function when the start action is triggered from CommonsShare
    auth_resp = check_authorization(request)
    if auth_resp.status_code != 200:
        return HttpResponseRedirect("/")
    else:
        # this is needed to strip out access token from URL
        return HttpResponseRedirect("/pivot_i2b2_transmart_copdgene/login_start/")

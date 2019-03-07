import hashlib
from json import load

from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import ValidationError

from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from pivot_i2b2_transmart_hcm.models import TransmartHCMConfig
from apps_core_services.utils import check_authorization
from pivot_orchestration_service.utils import validate_id, \
    deploy_appliance, PIVOTException

# Create your views here.


@login_required
def deploy(request):
    # view function when the deploy action is triggered from CommonsShare Apps Store from
    # which the user has already logged in to CommonsShare Apps Store directly
    conf_qs = TransmartHCMConfig.objects.all()

    if not conf_qs:
        config_file = 'pivot_i2b2_transmart_hcm/data/pivot_hcm.json'
        with open(config_file, 'r') as fp:
            conf_data = load(fp)
            if not 'id' in conf_data or not 'containers' in conf_data:
                errmsg = "PIVOT JSON Configuration file is not valid"
                messages.error(request, errmsg)
                return JsonResponse(data={'error': errmsg},
                                    status=HTTP_500_INTERNAL_SERVER_ERROR)
            TransmartHCMConfig.objects.create(data=conf_data)
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
        redirect_url = deploy_appliance(conf_data, check_res_avail=False)
        # new appliance has been created successfully
        return JsonResponse(status=HTTP_200_OK, data={'url': redirect_url})

    except PIVOTException as ex:
        return JsonResponse(data={'error': ex.message},
                            status=HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
def login_start(request):
    # view function when the start action is triggered from CommonsShare Apps Store from
    # which the user has already logged in to CommonsShare Apps Store directly
    return render(request, "pivot_i2b2_transmart_hcm/start.html", {})


def start(request):
    # view function when the start action is triggered from CommonsShare
    auth_resp = check_authorization(request)
    if auth_resp.status_code != 200:
        return HttpResponseRedirect("/")
    else:
        # this is needed to strip out access token from URL
        return HttpResponseRedirect("/pivot_i2b2_transmart_hcm/login_start/")

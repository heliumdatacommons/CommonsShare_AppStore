# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps_core_services.utils import check_authorization
from django.http import HttpResponseRedirect, JsonResponse
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR

from cloudtop_imagej import deployment

# Create your views here.
@login_required
def login_start(request):
    # view function when the start action is triggered from CommonsShare Apps Store from
    # which the user has already logged in to CommonsShare Apps Store directly
    print("ENTERING cloudtop_imagej/views.py::login_start(request)")
    redirect_url = deploy(request)
    messages.success(request, 'Launching CloudTop/ImageJ')
    return HttpResponseRedirect(redirect_url)


def start(request):
    print("entered here")
    # view function when the start action is triggered from CommonsShare
    auth_resp = check_authorization(request)
    if auth_resp.status_code != 200:
        return HttpResponseRedirect("/")
    else:
        # this is needed to strip out access token from URL
        return HttpResponseRedirect("/cloudtop_imagej/login_start/")


@login_required
def deploy(request):
    print("Entering cloudtop_imagej/views.py::deploy(request)")
    print("deploying service...")

    print(f"USERNAME: {request.user.username}")
    request.META['REMOTE_USER'] = request.user.username
    print(f"REQUEST META: {request.META}")
    request.session['REMOTE_USER'] = request.user.username

    try:
        redirect_url = deployment.deploy(request)
    except Exception as ex:
        return JsonResponse(data={'invalid ip_address or port from imagej deployment ': ex},
                            status=HTTP_500_INTERNAL_SERVER_ERROR)

    print("Exiting cloudtop_imagej/views.py::deploy(request)")
    return redirect_url

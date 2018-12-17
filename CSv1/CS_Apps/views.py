# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import requests
import json
import uuid
import datetime
from django.utils import timezone

now = timezone.now
# Create your views here.

def home_page_view(request):
    auth_resp = check_authorization(request)
    # print("auth_resp:", auth_resp)
    # print(auth_resp.status_code)
    if auth_resp.status_code != 200:
        return auth_resp
    return render(request, "home.html", {})

def get_auth_redirect():
    # set return_to to be where user is redirected back to upon successful login
    # it needs to be somewhere that will handle the access_token url parameter, which
    # can be the url of the current app, since check_authorization will check for it
    # right now this is restricted to domains matching '*.commonsshare.org'
    return_to = 'https://apps.commonsshare.org/apps/'

    url = 'https://auth.commonsshare.org/authorize?provider=auth0'
    url += '&scope=openid%20profile%20email'
    url += '&return_to=' + return_to
    resp = requests.get(url)
    print("resp:", resp)
    body = json.loads(resp.content.decode('utf-8'))
    print("body:", body)
    return HttpResponseRedirect(body['authorization_url'])


def check_authorization(request):
    print(request.GET.get("token"))
    skip_validate = False
    token = None
    r_invalid = get_auth_redirect()
    if 'HTTP_AUTHORIZATION' in request.META:
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return r_invalid
        terms = auth_header.split()
        if len(terms) != 2:
            return r_invalid
        elif terms[0] == 'Bearer':
            token = terms[1]
        else:
            return r_invalid
    elif 'token' in request.GET:
        token = request.GET.get('token')
        print(token)
    elif 'session_id' in request.session and request.session.get_expiry_date() >= now():
        # print(request.session.get_expiry_date())
        # print('session_id valid, expires in: ' + str((request.session.get_expiry_date() - now()).total_seconds()))
        skip_validate = True
    else:
        print('no authorization found')
        print(skip_validate)
        print("r_invalid", r_invalid)
        return r_invalid

    if not skip_validate:
        # need to check the token validity
        validate_url = 'https://auth.commonsshare.org/validate_token?access_token='
        resp = requests.get(validate_url + token)
        print(resp)
        if resp.status_code == 200:
            body = json.loads(resp.content.decode('utf-8'))
            if body.get('active', False) == True:
                # the token was valid, set a session
                print('received access token was valid, storing session')
                request.session['session_id'] = str(uuid.uuid4())
                request.session.set_expiry(datetime.timedelta(days=30).total_seconds())
                return JsonResponse(status=200, data={
                    'status_code': 200,
                    'message': 'Successful authentication',
                    'user': body.get('username')})
            # print(resp)
            # print(resp.content)
            r = JsonResponse(status=403, data={
                'status_code': 403,
                'message': 'Request forbidden'})
            return r
    else:
        # picked up existing valid session, no need to check again
        return JsonResponse(status=200, data={'status_code': 200, 'message': 'session was valid'})



def signin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('apps-view')
            else:
                message = "User is not active."
                return render(request, "sign_in.html", {'message': message})
        else:
            message = "Invalid login."
            return render(request, "sign_in.html", {'message': message})
    else:
        return render(request, "sign_in.html", {})


def signout_view(request):
    print(request)
    #print(request.GET['token'])
    #print(request.GET['session_id'])
    #del  request.GET['token']
    #del request.GET['session_id']
    #logout(request)
    return redirect('/')


def signup_view(request):
    if request.method == 'POST':

        fields_mapping = {}
        fields_mapping["first_name"] = "first_name"
        fields_mapping["last_name"] = "last_name"
        fields_mapping["username"] = "username"
        fields_mapping["email"] = "email"
        fields_mapping["password1"] = "password"

        params = dict()
        for field in fields_mapping:
            _field = fields_mapping[field]
            params[_field] = request.POST[field]

        user = User.objects.create_user(**params)
        user.save()
        return redirect("signin-view")

    else:
        return render(request, "sign_up.html", {})


# def _signup(request):

def show_apps(request):
    """
	"""
    return render(request, "apps.html", {})


def dashboard_view(request):
    return render(request, "dashboard.html", {})

def phenotype_analyze(request):
    print(request.GET)
    auth_resp = check_authorization(request)
    print("auth_resp:", auth_resp)
    print(type(auth_resp))
    print("="*100)
    print(request.META)
    if auth_resp.status_code != 200:
        return HttpResponseRedirect("/")
    else:
        body = json.loads(auth_resp.content.decode('utf-8'))
        if body['status_code'] == 200:
             return HttpResponseRedirect("https://monarchinitiative.org/analyze/phenotypes")

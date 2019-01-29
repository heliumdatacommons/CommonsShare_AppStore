# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
import json
from django.utils import timezone

from utils import check_authorization


now = timezone.now
# Create your views here.


def home_page_view(request):
    auth_resp = check_authorization(request)
    print("auth_resp:", auth_resp)
    print(auth_resp.status_code)
    if auth_resp.status_code != 200:
        return auth_resp
    return render(request, "home.html", {})


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

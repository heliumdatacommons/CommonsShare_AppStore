from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.apps import apps

from apps_core_services.utils import check_authorization, authenticate_user


# Create your views here.


def home_page_view(request):
    auth_resp = check_authorization(request)
    if auth_resp.status_code != 200:
        return auth_resp
    return render(request, "home.html", {})


def signout_view(request):
    #print(request)
    #print(request.GET['token'])
    #print(request.GET['session_id'])
    #del  request.GET['token']
    #del request.GET['session_id']
    #logout(request)
    return redirect('/')


def show_apps(request):
    token = request.GET.get('access_token', None)
    uname = request.GET.get('user_name', None)
    uemail = request.GET.get('email', None)

    apps_list = []

    for app_conf in apps.get_app_configs():
        try:
            url = app_conf.url
            logo = app_conf.logo
        except AttributeError:
            continue

        apps_list.append({'verbose_name': app_conf.verbose_name,
                          'url': url,
                          'logo': logo})

    if not token or not uname:
        auth_resp = check_authorization(request)
        if auth_resp.status_code != 200:
            return HttpResponseRedirect("/")
        else:
            return render(request, "apps.html", {'apps_list': apps_list})
    else:
        # requests coming from auth service return which already authenticated the user
        name = request.GET.get('name', None)
        ret_user = authenticate_user(request, username=uname, access_token=token,
                                name=name, email=uemail)
        if ret_user:
            return render(request, "apps.html", {'apps_list': apps_list})
        else:
            return HttpResponseBadRequest(
                'Bad request - no valid access_token or user_name is provided')

import requests
import uuid
import datetime
import json

from django.http import HttpResponseRedirect, JsonResponse
from django.conf import settings


def get_auth_redirect(request):
    # set return_to to be where user is redirected back to upon successful login
    # it needs to be somewhere that will handle the access_token url parameter, which
    # can be the url of the current app, since check_authorization will check for it
    # right now this is restricted to domains matching '*.commonsshare.org'
    return_to = '/apps/'
    return_url = '&return_to={}://{}/apps'.format(request.scheme, request.get_host())
    url = '{}authorize?provider=globus'.format(settings.OAUTH_SERVICE_SERVER_URL)
    url += '&scope=openid%20profile%20email'
    url += return_to
    auth_header_str = 'Basic {}'.format(settings.OAUTH_APP_KEY)
    resp = requests.get(url, headers={'Authorization': auth_header_str},
                        verify=False)
    print("resp:", resp)
    body = json.loads(resp.content.decode('utf-8'))
    print("body:", body)
    return HttpResponseRedirect(body['authorization_url'])


def check_authorization(request):
    print(request.GET.get("token"))
    token = request.GET.get("token")
    skip_validate = False
    if not token:
        r_invalid = get_auth_redirect(request)
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

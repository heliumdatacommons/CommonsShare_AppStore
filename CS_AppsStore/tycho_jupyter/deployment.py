import os
import yaml
from tycho.client import TychoClientFactory
from tycho.client import TychoApps
import time
import json


from django.http import HttpResponseRedirect

def deploy():
    try:
        client_factory = TychoClientFactory()
        client = client_factory.get_client()
        tycho_url = client.url
        print(f"TYCHO URL: {tycho_url}")
    except Exception as e:
        tycho_url = "http://localhost:5000/system"
        print(f"TYCHO URL: {tycho_url}")

    try:
        app = "jupyter-ds"
        tychoapps = TychoApps(app)
    except Exception as e:
        print(f"Exception: {e}")

    metadata = tychoapps.getmetadata()

    if 'System' in metadata.keys():
        structure = metadata['System']
    if 'Settings' in metadata.keys():
        settings = metadata['Settings']

    """ Load settings. """
    settings_dict = client.parse_env(settings)

    request = {
            "name": "jupyter-ds",
            "env": settings_dict,
            "system": structure,
            "user": settings_dict['REMOTE_HOST']
            "services": {
                "jupyter-datascience": {
                "port": settings_dict['HOST_PORT']
                }
             }
    }

    print(json.dumps(request))

    tycho_system = client.start(request)
    print(tycho_system)

    user = tycho_system.user
    guid = tycho_system.identifier
    status = tycho_system.status
    services = tycho_system.services

    print(status)

    if status != 'success':
        raise Exception("Error encountered while starting jupyter-datascience service: " + status)

    for service in services:
        name = service.name
        if name == 'jupyter-datascience':
            ip_address = service.ip_address
            port = settings_dict['HOST_PORT']
            print('ip_address: ' + ip_address)
            print('port: ' + str(port))

    if ip_address == '' or ip_address == '--':
        raise Exception("ip_address is invalid: " + ip_address)

    if port == '' or port == '--':
        raise Exception("port is invalid: " + port)

    redirect_url = 'http://' + ip_address + ':' + str(port)
    print('redirecting to ' + redirect_url)
    return redirect_url

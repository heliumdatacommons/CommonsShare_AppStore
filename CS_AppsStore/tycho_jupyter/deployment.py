import os
import yaml
from tycho.client import TychoClient, TychoClientFactory
import time

from django.http import HttpResponseRedirect

def deploy():

    client_factory = TychoClientFactory()
    #client = client_factory.get_client()

    client = TychoClient("http://35.199.30.174:8099")

    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "tycho_jupyter", "data")
    spec_path = os.path.join(data_dir,  "docker-compose.yaml")

    print(data_dir)

    """ Load settings. """
    env_file = os.path.join(data_dir, ".env")
    if os.path.exists(env_file):
        with open(env_file, 'r') as stream:
            settings = stream.read()

    settings_dict = client.parse_env(settings)

    """ Load docker-compose file consisting of system spec """
    with open(spec_path, "r") as stream:
        structure = yaml.load(stream)

    request = {
            "name": "jupyter-datascience",
            "env": settings_dict,
            "system": structure,
            "services": {
                "jupyter-datascience": {
                "port": settings_dict['HOST_PORT']
                }
             }
    }

    tycho_system = client.start(request)
    print(tycho_system)

    guid = tycho_system.identifier
    status = tycho_system.status
    services = tycho_system.services

    if status != 'success':
        raise Exception("Error encountered while starting jupyter-datascience service: " + status)

    for service in services:
        name = service.name
        if name == 'jupyter-datascienc':
            ip_address = service.ip_address
            port = service.port
            print('ip_address: ' + ip_address)
            print('port: ' + port)

    if ip_address == '' or ip_address == '--':
        raise Exception("ip_address is invalid: " + ip_address)

    if port == '' or port == '--':
        raise Exception("port is invalid: " + port)

    redirect_url = 'http://' + ip_address + ':' + str(port)
    print('redirecting to ' + redirect_url)
    return redirect_url

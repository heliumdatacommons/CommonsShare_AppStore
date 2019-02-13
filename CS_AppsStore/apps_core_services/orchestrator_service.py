import requests
from importlib import import_module
from rest_framework import status

from django.utils import timezone


def get_running_appliances_usage_status(status_model_path, request_url=''):
    """
    return usage status of all running appliances by querying the status model being passed in
    :param status_model_path: the path to be used to import the model
    :param request_url: optional parameter to check whether appliance has been deleted or not
    :return: context dictionary and error message if any
    """
    try:
        status_model = import_module(status_model_path)
    except ImportError as ex:
        return {}, 'model cannot be imported:' + ex.message

    fields = []
    for field in status_model._meta.get_field():
        fields.append(field.name)

    if 'user' not in fields or 'appliance_id' not in fields or 'status' not in fields:
        return {}, 'model does not have required attributes user, appliance_id, or status'

    context = {}

    for obj in status_model.objects.filter(status='R'):
        # check whether the appliance is really running since the appliance could be deleted
        # in PIVOT
        if request_url:
            url = request_url + obj.appliance_id
            get_response = requests.get(url)
            if get_response.status_code == status.HTTP_404_NOT_FOUND:
                # appliance has been deleted
                obj.staus = 'D'
                obj.end_timestamp = timezone.now()
                obj.save()




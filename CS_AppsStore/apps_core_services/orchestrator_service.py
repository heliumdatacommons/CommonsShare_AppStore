import requests
from importlib import import_module
from rest_framework import status

from django.utils import timezone


def get_running_appliances_usage_status(status_module_path, status_module_class, request_url=''):
    """
    return usage status of all running appliances by querying the status module class input.
    The class from the imported module must have the following fields:
    user, appliance_id, status, start_timestamp, end_timestamp. Additionally, the status_model
    could include optional memory, cpus, insts fields which represent resources allocated for
    the appliance, e.g., HAIL appliance
    :param status_module_path: the path to be used to import the module
    :param status_module_class: the class name to load from the module
    :param request_url: optional parameter to check whether appliance has been deleted or not
    :return: context dictionary and error message if any
    """
    try:
        status_module = import_module(status_module_path)
    except ImportError as ex:
        return {}, 'module cannot be imported:' + ex.message

    status_model = getattr(status_module, status_module_class)
    fields = []
    for field in status_model._meta.fields:
        fields.append(field.name)

    if 'user' not in fields or 'appliance_id' not in fields or 'status' not in fields:
        return {}, 'model does not have required attributes user, appliance_id, or status'

    context = {'usage_list': []}

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
            else:
                # appliance is live and being used, put it into context to send to caller
                context['usage_list'].append({
                    'username': obj.user.username,
                    'user_fullname': obj.user.get_full_name(),
                    'user_email': obj.user.email,
                    'appliance_id': obj.appliance_id,
                    'start_timestamp': obj.start_timestamp,
                    'insts': obj.insts if 'insts' in fields else None,
                    'memory': obj.memory if 'memory' in fields else None,
                    'cpus': obj.cpus if 'cpus' in fields else None,
                })
        else:
            # no need to check on whether appliance is live, just assume it is live
            context['usage_list'].append({
                'username': obj.user.username,
                'user_fullname': obj.user.get_full_name(),
                'user_email': obj.user.email,
                'appliance_id': obj.appliance_id,
                'start_timestamp': obj.start_timestamp,
                'insts': obj.insts if 'insts' in fields else None,
                'memory': obj.memory if 'memory' in fields else None,
                'cpus': obj.cpus if 'cpus' in fields else None,
            })

    return context, ''

import re
from json import dumps
import requests
import time
from importlib import import_module
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_200_OK, \
    HTTP_201_CREATED

from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError


class PIVOTResourceException(Exception):
    def __init__(self, message, code=None, params=None):
        super(PIVOTResourceException, self).__init__(self, message, code, params)
        self.message = message
        self.code = code
        self.params = params


class PIVOTException(Exception):
    def __init__(self, message, code=None, params=None):
        super(PIVOTException, self).__init__(self, message, code, params)
        self.message = message
        self.code = code
        self.params = params


def validate_id(id_in):
    """
    validate appliance or container id to make sure it only contain dash, underline, letters,
    and numbers required by pivot
    :param id_in: appliance id or container id to be validated
    :return: raise ValidationError upon failure
    """
    id_validation_failure_msg = 'appliance or container id {} failed validation - id can only ' \
                                'contain dash, underline, letters, and numbers'
    id_re = re.compile('^[a-zA-Z0-9_-]+$')
    if not id_re.match(id_in):
        # failure
        raise ValidationError(id_validation_failure_msg.format(id_in))
    # success
    return


def deploy_appliance(config_data, check_res_avail=False):
    """
    deploy appliance via PIVOT API
    :param config_data: appliance configuration data dict to send to PIVOT
    :param check_res_avail: optional with default being False indicating whether to check
    resource availability before requesting PIVOT to deploy the appliance
    :return: (True, redirect_url) upon success or raise PIVOTResourceException or PIVOTException
    upon failure
    """
    # check if appliance already exists, if yes, do redirect directly, if not, create a new one
    url = settings.PIVOT_URL + 'appliance'
    app_id = config_data['id']
    app_url = url + '/' + app_id
    get_response = requests.get(app_url)
    if get_response.status_code == HTTP_404_NOT_FOUND:
        if check_res_avail:
            # check whether there are enough resources available to create requested appliance
            response = requests.get(settings.PIVOT_URL + 'cluster')
            return_data = response.json()
            avail_cpus = 0
            avail_mems = 0
            for cluster in return_data:
                avail_cpus += cluster['resources']['cpus']
                avail_mems += cluster['resources']['mem']

            if avail_cpus < 1 or avail_mems < 1000:
                raise PIVOTResourceException('There are no resource available at the moment')

            # get requested cpus and mems
            for con in config_data['containers']:
                if con['id'] == 'workers':
                    num_insts = con['instances']
                    num_cpus = con['resources']['cpus']
                    mem_size = con['resources']['mem']

                    req_cpus = settings.INITIAL_COST_CPU + int(num_cpus) * int(num_insts)
                    req_mem = settings.INITIAL_COST_MEM + int(mem_size) * int(num_insts)

                    if req_cpus > avail_cpus or req_mem > avail_mems:
                        # there are not enough resources, notify users to reduce number of
                        # requested resources
                        err_msg = 'There are not enough resources available. Please reduce ' \
                                  'number of instances and resources requested to be within ' \
                                  'our available resource pool ({} CPUs and {}MB memory ' \
                                  'available at the moment).'
                        a_cpus = int(avail_cpus)
                        a_mems = int(avail_mems)
                        raise PIVOTResourceException(err_msg.format(a_cpus, a_mems))

                    break

        # request to create the appliance
        response = requests.post(url, data=dumps(config_data))
        if response.status_code == HTTP_409_CONFLICT:
            time.sleep(2)
            response = requests.post(url, data=dumps(config_data))

        if response.status_code != HTTP_200_OK and \
                        response.status_code != HTTP_201_CREATED:
            raise PIVOTException(response.text)

    # success, return redirct_url
    redirect_url = app_url + '/ui'
    return redirect_url


def get_running_appliances_usage_status(status_module_path, status_module_class, request_url=''):
    """
    return usage status of all running appliances by querying the status module class input.
    The status module class must inherit from the abstract ApplianceStatus model which defines
    required fields that apply to all PIVOT appliances. These fields are:
    user, appliance_id, status, start_timestamp, end_timestamp. The specific status module class
    can include additional fields that pertain to its specific needs. For example, HAIL cluster
    appliance status model includes additional memory, cpus, insts fields which represent resources
    that will be allocated for the appliance.
    :param status_module_path: the path to be used to import the module
    :param status_module_class: the class name to load from the module
    :param request_url: optional parameter to check whether appliance has been deleted or not
    :return: context dictionary upon success and raise ImportError or ValidationError upon failure
    """
    try:
        status_module = import_module(status_module_path)
    except ImportError as ex:
        raise ImportError('module cannot be imported: ' + ex.message)

    status_model = getattr(status_module, status_module_class)
    fields = []
    for field in status_model._meta.fields:
        fields.append(field.name)

    if 'user' not in fields or 'appliance_id' not in fields or 'status' not in fields or \
            'start_timestamp' not in fields or 'end_timestamp' not in fields:
        raise ValidationError('status model does not have required fields user, appliance_id, '
                              'status, start_timestamp, or end_timestamp')

    context = {'usage_list': []}

    for obj in status_model.objects.filter(status='R'):
        # check whether the appliance is really running since the appliance could be deleted
        # in PIVOT
        if request_url:
            url = request_url + obj.appliance_id
            get_response = requests.get(url)
            if get_response.status_code == HTTP_404_NOT_FOUND:
                # appliance has been deleted
                obj.status = 'D'
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

    return context

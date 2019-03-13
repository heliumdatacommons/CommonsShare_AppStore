import re
from json import dumps
import requests
import time
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_200_OK, \
    HTTP_201_CREATED

from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError

from pivot_orchestration_service.models import ApplianceStatus


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


def deploy_appliance(config_data):
    """
    deploy appliance via PIVOT API
    :param config_data: appliance configuration data dict to send to PIVOT
    :return: (redirect_url, cpus_consumed, mem_consumed) upon success or
    raise PIVOTResourceException or PIVOTException upon failure
    """
    # check if appliance already exists, if yes, do redirect directly, if not, create a new one
    try:
        url = settings.PIVOT_URL + 'appliance'
        app_id = config_data['id']
        app_url = url + '/' + app_id
        get_response = requests.get(app_url)
        redirect_url = app_url + '/ui'
        if get_response.status_code == HTTP_404_NOT_FOUND:
            # check whether there are enough resources available to create requested appliance
            response = requests.get(settings.PIVOT_URL + 'cluster')
            return_data = response.json()
            avail_cpus = 0
            avail_mems = 0
            avail_max_cpus = 0
            avail_max_mems = 0

            initial_cpu_cost_counted = False
            initial_mem_cost_counted = False
            for host in return_data:

                if not initial_cpu_cost_counted:
                    if host['resources']['cpus'] > settings.INITIAL_COST_CPU:
                        host['resources']['cpus'] -= settings.INITIAL_COST_CPU
                        initial_cpu_cost_counted = True
                if not initial_mem_cost_counted:
                    if host['resources']['mem'] > settings.INITIAL_COST_MEM:
                        host['resources']['mem'] -= settings.INITIAL_COST_MEM
                        initial_mem_cost_counted = True

                avail_cpus += host['resources']['cpus']
                avail_mems += host['resources']['mem']
                if host['resources']['cpus'] > avail_max_cpus:
                    avail_max_cpus = host['resources']['cpus']
                if host['resources']['mem'] > avail_max_mems:
                    avail_max_mems = host['resources']['mem']

            if avail_cpus < 1 or avail_mems < 1000:
                raise PIVOTResourceException('There are no resource available at the moment')

            total_req_cpus = settings.INITIAL_COST_CPU
            total_req_mem = settings.INITIAL_COST_MEM
            # get requested cpus and mems
            for con in config_data['containers']:
                if 'resources' in con:
                    req_cpus = con['resources']['cpus']
                    req_mem = con['resources']['mem']
                    total_req_cpus += req_cpus
                    total_req_mem += req_mem
                    if con['id'] == 'workers':
                        num_insts = con['instances']
                    else:
                        num_insts = 1
                    for i in range(num_insts):
                        if con['id'] == 'workers' and (req_cpus > avail_max_cpus or
                                                               req_mem > avail_max_mems):
                            # there are not enough resources, notify users to reduce number of
                            # requested resources
                            err_msg = 'There are not enough resources available. Please reduce ' \
                                      'number of instances and resources requested to be within ' \
                                      'our available resource pool ({} CPUs and {}MB memory ' \
                                      'available at the moment).'
                            a_cpus = int(avail_max_cpus)
                            a_mems = int(avail_max_mems)
                            raise PIVOTResourceException(err_msg.format(a_cpus, a_mems))

                        resource_checked = False
                        for host in return_data:
                            avail_cpus_host = host['resources']['cpus']
                            avail_mems_host = host['resources']['mem']
                            if req_cpus <= avail_cpus_host and req_mem <= avail_mems_host:
                                # deduct the requested resource from available resource pool and
                                # break out host check to continue with next container check
                                host['resources']['cpus'] -= req_cpus
                                host['resources']['mem'] -= req_mem
                                resource_checked = True
                                break
                        if not resource_checked:
                            if con['id'] == 'workers':
                                # there are not enough resources, notify users to reduce number of
                                # requested resources
                                err_msg = 'There are not enough resources available. Please reduce ' \
                                          'number of instances and resources requested and try ' \
                                          'again.'
                                raise PIVOTResourceException(err_msg)
                            else:
                                # there are not enough resources, notify users to reduce number of
                                # requested resources
                                err_msg = 'There are not enough resources available. Please ' \
                                          'email protocopdgenehelp@lists.renci.org to get ' \
                                          'more details on the resource availability.'
                                raise PIVOTResourceException(err_msg)

            # request to create the appliance
            response = requests.post(url, data=dumps(config_data))
            if response.status_code == HTTP_409_CONFLICT:
                time.sleep(2)
                response = requests.post(url, data=dumps(config_data))

            if response.status_code != HTTP_200_OK and \
                            response.status_code != HTTP_201_CREATED:
                raise PIVOTException(response.text)

            # success, return redirct_url
            return redirect_url, total_req_cpus, total_req_mem
        else:
            # appliance already exists, no additional resource is requested
            return redirect_url, -1, -1
    except Exception as ex:
        raise PIVOTException(ex)


def get_running_appliances_usage_status(request_url=''):
    """
    return usage status of all running appliances by querying ApplianceStatus model which defines
    required fields that apply to all PIVOT appliances. These fields are:
    user, appliance_id, status, start_timestamp, end_timestamp, cpus, and memory.
    :param request_url: optional parameter to check whether appliance has been deleted or not
    :return: context dictionary upon success and raise ImportError or ValidationError upon failure
    """
    context = {'usage_list': []}

    for obj in ApplianceStatus.objects.filter(status='R'):
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
                    'memory': obj.memory,
                    'cpus': obj.cpus,
                })
        else:
            # no need to check on whether appliance is live, just assume it is live
            context['usage_list'].append({
                'username': obj.user.username,
                'user_fullname': obj.user.get_full_name(),
                'user_email': obj.user.email,
                'appliance_id': obj.appliance_id,
                'start_timestamp': obj.start_timestamp,
                'memory': obj.memory,
                'cpus': obj.cpus,
            })

    return context

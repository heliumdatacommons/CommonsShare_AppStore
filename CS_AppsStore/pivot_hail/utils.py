from json import load

from pivot_hail.models import HailConfig


def get_hail_start_context(request):
    """
    return error message or context retrieved from json configuration for starting HAIL cluster
    appliance
    :param request: request object
    :return: context or error message in dict format
    """
    conf_qs = HailConfig.objects.all()
    if not conf_qs:
        config_file = 'pivot_hail/data/pivot_hail.json'
        with open(config_file, 'r') as fp:
            p_data = load(fp)
            if not 'id' in p_data or not 'containers' in p_data:
                context = {
                    'error': 'PIVOT JSON Configuration file is not valid'
                }
                return context

            HailConfig.objects.create(data=p_data)
    else:
        p_data = HailConfig.objects.all().first().data

    # get default value to show on the start page for users to override as needed
    context = {}
    for con in p_data['containers']:
        if con['id'] == 'workers':
            insts = con['instances']
            cpus = con['resources']['cpus']
            mems = con['resources']['mem']
            context = {
                'num_instances': str(insts),
                'num_cpus': str(cpus),
                'mem_size': str(mems)
            }
            break

    return context

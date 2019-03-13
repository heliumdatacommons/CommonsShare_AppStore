from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseServerError
from django.core.exceptions import ValidationError
from django.conf import settings

from pivot_orchestration_service.utils import get_running_appliances_usage_status


# Create your views here.


@login_required()
def status(request):
    url = settings.PIVOT_URL + 'appliance/'
    try:
        context = get_running_appliances_usage_status(request_url=url)
        return render(request, "pivot_orchestration_service/status.html", context)
    except (ImportError, ValidationError) as ex:
        return HttpResponseServerError(ex.message)

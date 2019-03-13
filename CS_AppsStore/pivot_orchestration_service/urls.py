from django.conf.urls import url
from pivot_orchestration_service import views


urlpatterns = [
    url(r'^status/$', views.status, name='pivot_status'),
]

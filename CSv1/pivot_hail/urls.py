from django.conf.urls import url
from pivot_hail import views


urlpatterns = [
    url(r'^deploy/$', views.deploy, name='hail_deploy'),
    url(r'^start/$', views.start, name='hail_start'),
]

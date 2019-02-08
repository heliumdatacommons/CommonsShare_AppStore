from django.conf.urls import url
from pivot_hail import views


urlpatterns = [
    url(r'^deploy/$', views.deploy, name='hail_deploy'),
    url(r'^login_start/$', views.login_start, name='hail_login_start'),
    url(r'^start/$', views.start, name='hail_start'),
]

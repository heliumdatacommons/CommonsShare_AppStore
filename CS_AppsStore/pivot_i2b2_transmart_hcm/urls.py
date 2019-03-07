from django.conf.urls import url
from pivot_i2b2_transmart_hcm import views


urlpatterns = [
    url(r'^deploy/$', views.deploy, name='hcm_deploy'),
    url(r'^login_start/$', views.login_start, name='hcm_login_start'),
    url(r'^start/$', views.start, name='hcm_start'),
]

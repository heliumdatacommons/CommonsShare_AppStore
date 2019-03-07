from django.conf.urls import url
from pivot_i2b2_transmart_copdgene import views


urlpatterns = [
    url(r'^deploy/$', views.deploy, name='copdgene_deploy'),
    url(r'^login_start/$', views.login_start, name='copdgene_login_start'),
    url(r'^start/$', views.start, name='copdgene_start'),
]

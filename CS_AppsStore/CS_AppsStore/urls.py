"""CS_AppsStore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from apps_core_services import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^signout_view$', views.signout_view),
    url(r'^apps/$', views.show_apps, name='apps-view'),
    url(r'^login_apps/$', views.login_show_apps, name='login-apps-view'),
    url(r'^$', views.home_page_view, name='home-page-view'),
]

urlpatterns += [
    url('^pivot/', include('pivot_orchestration_service.urls')),
    url('^pivot_hail/', include('pivot_hail.urls')),
    url('^phenotype/', include('phenotype.urls')),
    url('^pivot_i2b2_transmart_copdgene/', include('pivot_i2b2_transmart_copdgene.urls')),
    url('^pivot_i2b2_transmart_hcm/', include('pivot_i2b2_transmart_hcm.urls')),
]

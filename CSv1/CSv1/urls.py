"""CSv1 URL Configuration

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
from django.conf.urls import url
from django.contrib import admin
from CS_Apps import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^signout_view$', views.signout_view),
    url(r'^accounts/signup/$', views.signup_view),
    url(r'^accounts/signin/$', views.signin_view, name='signin-view'),
    url(r'^apps/$', views.show_apps, name='apps-view'),
    url(r'^$', views.home_page_view, name='home-page-view'),
    url(r'^phenotype$', views.phenotype_analyze, name="phenotype_analyze"),
]

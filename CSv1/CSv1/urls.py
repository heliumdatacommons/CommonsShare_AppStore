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
    #url(r'^accounts/login/$', views.signin_view, name='signin-view'),
    url(r'^signout_view$', views.signout_view),
    url(r'^accounts/signup/$', views.signup_view),
    url(r'^apps/$', views.show_apps, name='apps-view'),
    url(r'^$', views.home_page_view, name='home-page-view'),
    #url(r'^phenotype/?husername=${HS_USR_NAME}&token=${HS_USR_TOKEN}&resourcetype=${HS_RES_TYPE}&resourceid=${HS_RES_ID}$',views.phenotype_analyze, name="phenotype_analyze"),
    url(r'^phenotype$', views.phenotype_analyze, name="phenotype_analyze"),
    #url(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    #url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    #url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    #url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

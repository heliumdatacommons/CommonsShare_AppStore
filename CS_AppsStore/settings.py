"""
Django settings for CS_AppsStore project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

#local_settings_module = os.environ.get('LOCAL_SETTINGS', 'CS_AppsStore.local_settings')
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
os.environ['REMOTE_USER'] = "ana_muk1"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n2mb4kf5(_%_p!raq@e58ub+mws^!a+zvn4!#a1ijm(5cob_d*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    #'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps_core_services',
    'phenotype',
    'tycho_jupyter',
    'tycho_nextflow',
    'cloudtop_imagej',
    #'oidc_provider'
    # The following apps are required:
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'rest_auth.registration',
    # ... include the providers you want to enable:
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    #'allauth.socialaccount.providers.jupyterhub',
    #'allauth.socialaccount.providers.openid',
    #'allauth.socialaccount.providers.orcid',
    'bootstrapform'
]


SITE_ID = 4


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    #'oidc_provider.middleware.SessionManagementMiddleware',
]

#django allauth configuration

ACCOUNT_EMAIL_REQUIRED = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS =1
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 3
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 86400 # 1 day in seconds
ACCOUNT_LOGOUT_REDIRECT_URL ='/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/email/' 
# redirects to /accounts/profile by default
#ACCOUNT_FORMS = {
#'signup': 'CS_AppsStore.forms.CustomSignupForm',
#}
#ACCOUNT_ADAPTER = 'CS_AppsStore.adapter.RestrictEmailAdapter'

#django rest-auth configuration

# django-rest-auth configuration

#REST_SESSION_LOGIN = False
#OLD_PASSWORD_FIELD_ENABLED = True

#REST_AUTH_SERIALIZERS = {
  #  "TOKEN_SERIALIZER": "accounts.api.serializers.TokenSerializer",
 #   "USER_DETAILS_SERIALIZER": "accounts.api.serializers.UserDetailSerializer",
#}

#REST_AUTH_REGISTER_SERIALIZERS = {
#    "REGISTER_SERIALIZER": "accounts.api.serializers.CustomRegisterSerializer"
#}

#REST_FRAMEWORK = {
#    'DEFAULT_AUTHENTICATION_CLASSES': [
#        'rest_framework_simplejwt.authentication.JWTAuthentication',
#    ],
#}

AUTHENTICATION_BACKENDS = (
#    'apps_core_services.backends.oauth.OAuth',
# Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.RemoteUserBackend',
    # modelbackend added as a fallback to remote user mode
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"

SOCIALACCOUNT_QUERY_EMAIL = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SOCIALACCOUNT_PROVIDERS = \
    {'google':
        {'SCOPE': ['profile', 'email'],
         'AUTH_PARAMS': {'access_type': 'online'}}}

ROOT_URLCONF = 'CS_AppsStore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
              # `allauth` needs this from django
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'CS_AppsStore.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = 'allauth.socialaccount.context_processors.socialaccount'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
 'default': {
       'ENGINE': 'django.db.backends.sqlite3',
       'NAME': os.path.join(BASE_DIR, 'DATABASE.sqlite3'),
   }
}

##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.
#local_settings = __import__(local_settings_module, globals(), locals(), ['*'])
#for k in dir(local_settings):
#    locals()[k] = getattr(local_settings, k)

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL.strip("/"))

# PIVOT HAIL APP specific settings
INITIAL_COST_CPU = 6
INITIAL_COST_MEM = 6 # in MB

# phenotype specific settings
PHENOTYPE_REDIRECT_URL = "https://monarchinitiative.org/analyze/phenotypes"

OIDC_SESSION_MANAGEMENT_ENABLE = True
SITE_URL = 'http://localhost:8000'

LOGIN_REDIRECT_URL = '/login_apps/'

REST_USE_JWT = True

DEFAULT_AUTHENTICATION_CLASSES = [
            'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
            'rest_framework.authentication.BasicAuthentication',

    ]

"""
Django settings for appsite project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import sys
from pathlib import Path

# Pycactvs needs that
sys.setdlopenflags(os.RTLD_GLOBAL|os.RTLD_NOW)

from pycactvs import cactvs
CACTVS_SETTINGS = cactvs

propertypath = list(CACTVS_SETTINGS['propertypath'])
propertypath.insert(1, '/home/app/cactvsenv/prop')

CACTVS_SETTINGS['python_object_autodelete'] = True
CACTVS_SETTINGS['lookup_hosts'] = []
CACTVS_SETTINGS['propertypath'] = tuple(propertypath)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-45!c6!i^(_tq(2y4(da6w5c=%abopm1h$599$x@+*c-jwts$&u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# that is for development and might delete data!
INIT_SYSTEM = True

ALLOWED_HOSTS = os.environ['APP_VIRTUAL_HOSTNAME'].split(",")


# Application definition

INSTALLED_APPS = [
    'database.apps.DatabaseConfig',
    'structure.apps.StructureConfig',
    'neon.apps.NeonConfig',
    'resolver.apps.ResolverConfig',
    'etl.apps.ETLConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',#
    'django.contrib.staticfiles',
    'django_celery_results',
    'rest_framework',
#    'rest_framework_json_api',
    'django_filters',
    'crispy_forms',
    'multiselectfield',
    'dbbackup',
    'compressor',
    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'appsite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'templates',
            'structure/templates',
            'resolver/templates',
            'neon/templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'appsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ['POSTGRES_USER'],
            'USER':  os.environ['POSTGRES_USER'],
            'PASSWORD': os.environ['POSTGRES_PASSWORD'],
            'HOST': os.environ['POSTGRES_HOST'],
            'PORT': os.environ['POSTGRES_PORT']
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://cirx-cache:6379',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join("/home/app", "static/")
STATICFILES_FINDERS=(
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

MEDIA_ROOT = os.path.join("/home/app", "media/")
MEDIA_URL = "/media/"


#### JSON API

REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'rest_framework_json_api.exceptions.exception_handler',
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework_json_api.pagination.JsonApiPageNumberPagination',
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework_json_api.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework_json_api.renderers.JSONRenderer',
        #'resolver.renderers.ResolverAPIRenderer',
    ),
    'DEFAULT_METADATA_CLASS': 'rest_framework_json_api.metadata.JSONAPIMetadata',
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_json_api.filters.QueryParameterValidationFilter',
        'rest_framework_json_api.filters.OrderingFilter',
        'rest_framework_json_api.django_filters.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ),
    'SEARCH_PARAM': 'filter[search]',
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework_json_api.renderers.JSONRenderer',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'vnd.api+json',
}

JSON_API_FORMAT_FIELD_NAMES = 'camelize'

### LOGGING

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {process} : {funcName} | {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/home/app/logging/cirx.log',
            'formatter': 'verbose'
        },
        'celery': {
            'class': 'logging.FileHandler',
            'filename': '/home/app/logging/celery.log',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'cirx': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery.task': {
            'handlers': ['console', 'celery'],
            'level': 'INFO',
        },
    },
}

### CELERY SETTINGS

CELERY_BROKER_URL = 'redis://cirx-cache:6379'

CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 10000000}

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

#CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_RESULT_BACKEND = 'django-cache'
CELERY_TIMEZONE = "Europe/Berlin"
CELERY_MAX_TASKS_PER_CHILD = 1

CELERYD_HIJACK_ROOT_LOGGER = False
#CELERYD_MAX_TASKS_PER_CHILD = 1


# CIR Settings

CIR_AVAILABLE_RESOLVERS = [
    #'smiles',
    #'stdinchikey',
    #'stdinchi',
    #'ncicadd_identifier',
    #'hashisy',
    #'chemspider_id',
    #'chemnavigator_sid',
    #'pubchem_sid',
    #'emolecules_vid',
    #'ncicadd_rid',
    #'ncicadd_cid',
    #'ncicadd_sid',
    #'cas_number',
    #'nsc_number',
    #'zinc_code',
    #'opsin',
    #'chemspider_name',
    #'name_pattern',
    'name',
    #'SDFile',
    #'minimol',
    #'packstring',
]

CIR_FILESTORE_ROOT = os.path.join("/filestore")
CIR_INSTORE_ROOT = os.path.join("/instore")


### THE WE HAVE TO GET RID OF THIS SECTION

#BASE_URL =  \
#    '/chemical'
#STRUCTURE_BASE_URL=BASE_URL + '/structure'

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/home/app/backup/'}

if DEBUG:
    import os  # only if you haven't already imported this
    import socket  # only if you haven't already imported this
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
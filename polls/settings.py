"""
Django settings for polls project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'm=%-=98*jf5hjfyjui+%5azyzr4z-$3b)q$5#1ys@6#!-#!n&e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
ALLOWED_HOSTS = ['*']

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True


# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'polls',
]

MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

ROOT_URLCONF = 'polls.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'polls.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(conn_max_age=500),
}


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'


# Cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'pollsapi',
    }
}

CACHE_MIDDLEWARE_SECONDS = 10


def get_env(key, default=True):
    value = os.environ.get(key, default)
    return (
        value is True
        or value.lower() == 'true'
        or value == '1'
        or value.lower() == 'yes'
    )


# Security Middleware
if not DEBUG:
    SECURE_SSL_REDIRECT = get_env('SECURE_SSL_REDIRECT')


# Polls API Features

# Enables the ability to create a question
CAN_CREATE_QUESTION = get_env('POLLS_CAN_CREATE_QUESTION')

# Enables the ability to delete a question
CAN_DELETE_QUESTION = get_env('POLLS_CAN_DELETE_QUESTION')

# Enables the ability to vote on a question
CAN_VOTE_QUESTION = get_env('POLLS_CAN_VOTE_QUESTION')


X_FRAME_OPTIONS = 'DENY'

# CORS Headers

CORS_ORIGIN_ALLOW_ALL = True

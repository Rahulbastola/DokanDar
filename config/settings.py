"""
Django settings for config project.
"""

from datetime import timedelta
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',

    'users',
    'catalog',
    'orders',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend' / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://github.com/microsoft/mssql-django

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': config('DB_NAME'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default=''),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'OPTIONS': {
            'driver': config('DB_DRIVER', default='ODBC Driver 17 for SQL Server'),
            'trusted_connection': config('DB_TRUSTED_CONNECTION', default='yes'),
            'extra_params': config('DB_EXTRA_PARAMS', default='TrustServerCertificate=yes'),
        },
    }
}


# Custom user model

AUTH_USER_MODEL = 'users.User'


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static & media files

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'frontend' / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Django REST Framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=6),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}


# CORS (vanilla JS frontend calling the API from the same or another origin)

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='', cast=Csv())


# eSewa payment gateway (sandbox/UAT by default)

ESEWA_MERCHANT_CODE = config('ESEWA_MERCHANT_CODE', default='EPAYTEST')
ESEWA_SECRET_KEY = config('ESEWA_SECRET_KEY', default='8gBm/:&EnhH.1/q')
ESEWA_PAYMENT_URL = config(
    'ESEWA_PAYMENT_URL', default='https://rc-epay.esewa.com.np/api/epay/main/v2/form'
)
ESEWA_STATUS_CHECK_URL = config(
    'ESEWA_STATUS_CHECK_URL', default='https://rc.esewa.com.np/api/epay/transaction/status/'
)
ESEWA_SUCCESS_URL = config(
    'ESEWA_SUCCESS_URL', default='http://127.0.0.1:8000/api/payment/esewa/success/'
)
ESEWA_FAILURE_URL = config(
    'ESEWA_FAILURE_URL', default='http://127.0.0.1:8000/api/payment/esewa/failure/'
)

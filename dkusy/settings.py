import codecs
import os
from configparser import RawConfigParser


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


config = RawConfigParser()
config.read_file(codecs.open(os.path.join(BASE_DIR, 'config.ini'), 'r', 'utf-8'))

SECRET_KEY = config.get('GENERAL', 'SECRET_KEY')

DEBUG = config.getboolean('GENERAL', 'ALLOW_DEBUG')

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

INTERNAL_IPS = [
    '127.0.0.1'
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'debug_toolbar',
    'rest_framework',
    'apps.bushelper',
    'apps.users'
]
ROOT_URLCONF = 'dkusy.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'apps')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.common.context_processors.profile',
            ],
        },
    },
]

WSGI_APPLICATION = 'dkusy.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': config.get('DATABASE', 'ENGINE'),
        'NAME': os.path.join(BASE_DIR, config.get('DATABASE', 'NAME')),
    }
}

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

LANGUAGE_CODE = 'pl-pl'

TIME_ZONE = 'Europe/Warsaw'

USE_I18N = True

USE_L10N = True

USE_TZ = True


TIME_INPUT_FORMATS = [
    '%H:%M',
]

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

EMAIL = config.get('SMTP', 'EMAIL_ADDRESS')
EMAIL_PASSWORD = config.get('SMTP', 'EMAIL_HOST_PASSWORD')


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5
}
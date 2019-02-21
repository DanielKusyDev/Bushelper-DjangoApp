from .base import *

DEBUG = False
ALLOWED_HOSTS = ['bushelper.herokuapp.com', 'bushelper.pl', '*']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
STATICFILES_STORAGE = 'custom_storage.custom_azure.PublicAzureStorage'
AZURE_ACCOUNT_NAME = "djangostorage"
AZURE_ACCOUNT_KEY = "hLHJ2aeFszT3At++BoABlZnzdWKTX3/8bPNUj69XAiXG0rKLzxdv4Ds1FCeQvjeIHgqaqmDdEPQxTBOypZvEkw=="
AZURE_CONTAINER = "djangostoragecontainer"

import dj_database_url

db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)
DATABASES['default']['CONN_MAX_AGE'] = 500

CORS_REPLACE_HTTPS_REFERER = True
HOST_SCHEME = "https://"
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 1000000
SECURE_FRAME_DENY = True

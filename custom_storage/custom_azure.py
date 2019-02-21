from storages.backends.azure_storage import AzureStorage
from dkusy.settings.production import *


class PublicAzureStorage(AzureStorage):
    account_name = AZURE_ACCOUNT_NAME
    account_key = AZURE_ACCOUNT_KEY
    azure_container = AZURE_CONTAINER
    expiration_secs = None
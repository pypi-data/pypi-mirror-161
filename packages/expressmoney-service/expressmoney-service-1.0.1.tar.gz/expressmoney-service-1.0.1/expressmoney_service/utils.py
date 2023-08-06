from google.cloud import secretmanager
from google.cloud import secretmanager_v1

secret_manager_client = secretmanager.SecretManagerServiceClient()
access_secret_version = secretmanager_v1.types.service.AccessSecretVersionRequest()


def get_secret(secret_key: str):
    name = f'projects/829013617684/secrets/{secret_key}/versions/1'
    access_secret_version.name = name
    return secret_manager_client.access_secret_version(request=access_secret_version).payload.data.decode("utf-8")

from models.client_models import Client
import secrets

from models.util_models import ClientCredentialType

def get_profile_default_from_client(client: Client, key: str) -> any:
    """
    Get the default value for the given key from a client.

    Args:
        key (str): The key of the default value.

    Returns:
        any: The default value for the given key. None if the key does not exist.
    """
    return client.profile_defaults.get(key, None)

def generate_client_credential(credential_type: ClientCredentialType) -> str:
    """
    Generate a hex client credential for a client.

    Args:
        credential_type (ClientCredentialType): The type of credential to generate.

    Returns:
        str: The generated client credential.
    """
    return secrets.token_hex(credential_type.value)
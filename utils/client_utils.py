from models.client_models import Client


def get_profile_default_from_client(client: Client, key: str) -> any:
    """
    Get the default value for the given key from a client.

    Args:
        key (str): The key of the default value.

    Returns:
        any: The default value for the given key. None if the key does not exist.
    """
    return client.profile_defaults.get(key, None)
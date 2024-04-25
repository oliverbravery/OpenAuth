from models.client_models import Client
from common import db_manager

def validate_client_credentials(client_id: str, client_secret: str) -> bool:
    """
    Validate the client credentials.

    Args:
        client_id (str): The client id of the application.
        client_secret (str): The client secret of the application.

    Returns:
        bool: True if the client credentials are valid, False otherwise.
    """
    client: Client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return False
    return client.client_secret == client_secret

def valid_client_scopes(client_id: str, scopes: list[str]) -> bool:
    """
    Check that the client has the requested scopes.

    Args:
        client_id (str): Client id of the application.
        scopes (list[str]): List of scopes requested by the client.

    Returns:
        bool: True if the client scopes are valid, False otherwise.
    """
    client: Client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return False
    client_scopes: list[str] = list(client.scopes.keys())
    return all(scope in client_scopes for scope in scopes)
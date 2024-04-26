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

def valid_request_scopes(client_id: str, scopes: list[str]) -> bool:
    """
    Check that the requested scopes are valid for the client.

    Args:
        client_id (str): Client id of the application.
        scopes (list[str]): List of scopes requested by the client.

    Returns:
        bool: True if the requested scopes are valid, False otherwise.
    """
    client: Client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return False
    exists: bool = False
    for req_scope in scopes:
        exists = False
        for c_scope in client.scopes:
            if req_scope == c_scope.name:
                exists = True
        if not exists: return False
    return True
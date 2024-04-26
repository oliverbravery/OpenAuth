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
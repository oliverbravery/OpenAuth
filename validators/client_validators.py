from models.account_models import Account, AccountRole
from models.client_models import Client, ClientDeveloper
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

def validate_client_developers(client: Client) -> bool:
    """
    Validate that the client's developers exist as developer accounts and that their scopes are developer only scopes in their client.
    
    NOTE: 
    - This function returns False if the scopes are not associated with the specified client.
    - Scopes in the ClientDeveloper are assumed to be of the same client so are NOT in the <client_id>:<scope> format.
    
    Args:
        client (Client): The client to validate.

    Returns:
        bool: True if the client developers are valid, False otherwise.
    """
    client_developer_scope_names: list[str] = [scope.name for scope in client.scopes if scope.developer_only]
    for developer in client.developers:
        developer_account: Account = db_manager.accounts_interface.get_account(username=developer.username)
        if not developer_account or developer_account.account_role != AccountRole.DEVELOPER: return False
        for dev_scope in developer.scopes:
            if dev_scope not in client_developer_scope_names: return False
    return True
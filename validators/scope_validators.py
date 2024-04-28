from models.client_models import Client
from models.scope_models import ClientScope, ProfileScope
from common import db_manager


def valid_request_scopes(scopes: list[ProfileScope]) -> bool:
    """
    Check that the requested scopes are valid scopes that exist.
    
    NOTE: Scopes that are developer only are not allowed to be requested.

    Args:
        scopes (list[ProfileScope]): List of requested scopes to validate.

    Returns:
        bool: True if the requested scopes are valid, False otherwise.
    """
    client_to_scope: dict[str, list[ProfileScope]] = {scope.client_id: [] for scope in scopes}
    for scope in scopes:
        client_to_scope[scope.client_id].append(scope)
    for client_id, scope_list in client_to_scope.items():
        str_scope_list: list[str] = [scope.scope for scope in scope_list]
        client: Client = db_manager.clients_interface.get_client(client_id=client_id)
        if not client: return False
        matching_client_scopes: list[ClientScope] = [scope for scope in client.scopes if scope.name in str_scope_list and not scope.developer_only]
        if len(matching_client_scopes) != len(scope_list): return False
    return True
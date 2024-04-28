from models.client_models import Client
from models.scope_models import ProfileScope
from common import db_manager


def valid_request_scopes(scopes: list[ProfileScope]) -> bool:
    """
    Check that the requested scopes are valid scopes that exist.

    Args:
        scopes (list[ProfileScope]): List of requested scopes to validate.

    Returns:
        bool: True if the requested scopes are valid, False otherwise.
    """
    client_to_scope: dict[str, list[ProfileScope]] = {scope.client_id: [] for scope in scopes}
    for scope in scopes:
        client_to_scope[scope.client_id].append(scope)
    for client_id, scope_list in client_to_scope.items():
        client: Client = db_manager.clients_interface.get_client(client_id=client_id)
        if not client: return False
        client_scope_names: list[str] = [scope.name for scope in client.scopes]
        for requested_scope in scope_list:
            if requested_scope.scope not in client_scope_names: return False
    return True
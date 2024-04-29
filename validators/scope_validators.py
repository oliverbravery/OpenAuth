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

def check_client_scopes_have_unique_names(scopes: list[ClientScope]) -> bool:
    """
    Check that the client's scopes have unique names.

    Args:
        scopes (list[ClientScope]): The scopes to check.

    Returns:
        bool: True if the client's scopes have unique names, False otherwise.
    """
    scope_names: list[str] = [scope.name for scope in scopes]
    return len(set(scope_names)) == len(scope_names)

def validate_client_scopes(client: Client) -> bool:
    """
    Validate that the client's scopes are unique and that the associated attributes exist in the client's metadata. 
    
    NOTE: If there are duplicate attributes for a scope this function will return False.

    Args:
        client (Client): The client to validate.

    Returns:
        bool: True if the client's scopes are valid, False otherwise.
    """
    if not check_client_scopes_have_unique_names(scopes=client.scopes.client_scopes): return False
    metadata_attribute_names: list[str] = [metadata_attribute.name for metadata_attribute in client.profile_metadata_attributes]
    for scope in client.scopes.client_scopes:
        scope_attribute_names: list[str] = [scope_attribute.attribute_name for scope_attribute in scope.associated_attributes]
        if len(scope_attribute_names) != len(set(scope_attribute_names)): return False
        if not all([attribute in metadata_attribute_names for attribute in scope_attribute_names]): return False
    return True
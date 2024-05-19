from models.client_models import Client
from models.scope_models import ClientScope, ProfileScope
from common import db_manager


def valid_request_scopes(scopes: list[ProfileScope], developer_only: bool = None, 
                         shareable_only:bool=None) -> bool:
    """
    Check that the requested scopes are valid scopes that exist.
    
    NOTE: Scopes that are developer only are not allowed to be requested.

    Args:
        scopes (list[ProfileScope]): List of requested scopes to validate.
        developer_only (bool, optional): If True, only developer only scopes are allowed. Defaults to None (do not check).
        shareable_only (bool, optional): If True, only shareable scopes are allowed. Defaults to None (do not check).

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
        matching_client_scopes: list[ClientScope] = []
        for scope in client.scopes:
            if scope.name in str_scope_list:
                if (developer_only is not None and scope.developer_only != developer_only) or (shareable_only is not None and scope.shareable != shareable_only):
                    pass
                else:
                    matching_client_scopes.append(scope)
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
    if not check_client_scopes_have_unique_names(scopes=client.scopes): return False
    metadata_attribute_names: list[str] = [metadata_attribute.name for metadata_attribute in client.profile_metadata_attributes]
    for scope in client.scopes:
        scope_metadata_attribute_names: list[str] = [scope_attribute.attribute_name for scope_attribute in scope.associated_attributes.client_attributes]
        if len(scope_metadata_attribute_names) != len(set(scope_metadata_attribute_names)): return False
        if not all([attribute in metadata_attribute_names for attribute in scope_metadata_attribute_names]): return False
    return True
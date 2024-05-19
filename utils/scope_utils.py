from models.client_models import Client
from models.scope_models import ClientScope, ProfileScope, ScopeAccessType


def profile_scope_to_str(scope: ProfileScope) -> str:
    """
    Get the profile scope as a string. Combines the client_id and the scope as a string (client_id.scope).
    
    Returns:
        str: The scope as a string.
    """
    return f"{scope.client_id}.{scope.scope}"

def str_to_profile_scope(scope: str) -> ProfileScope:
    """
    Converts a combined scope string (client_id.scope) to a ProfileScope object.

    Args:
        scope (str): The combined scope string.

    Returns:
        ProfileScope: The ProfileScope object. None if the scope is invalid format.
    """
    split_scope: list[str] = scope.split(".")
    if split_scope and len(split_scope) == 2:
        return ProfileScope(client_id=split_scope[0], scope=split_scope[1])
    return None

def scopes_to_profile_scopes(scope_name_list: list[str]) -> list[ProfileScope]:
    """
    Converts a list of scopes as strings to a list of profile scopes.
    
    NOTE: Assumes that the scopes are valid.

    Args:
        scope_name_list (list[str]): The list of scope names.

    Returns:
        list[ProfileScope]: The list of profile scopes. None if a scope is in a invalid format.
    """
    profile_scopes: list[ProfileScope] = []
    for scope_str in scope_name_list:
        profile_scope: ProfileScope = str_to_profile_scope(scope=scope_str)
        if profile_scope is None: return None
        profile_scopes.append(profile_scope)
    return profile_scopes

def str_to_list_of_profile_scopes(scopes_str_list: str) -> list[ProfileScope]:
    """
    Converts a space seperated list as a string to a list of profile scopes.
    
    NOTE: Assumes that the scopes are valid.

    Args:
        scopes_str_list (str): The space separated list of scope names.

    Returns:
        list[ProfileScope]: The list of profile scopes.
    """
    if scopes_str_list == "": return []
    split_string: list[str] = scopes_str_list.split(" ")
    return scopes_to_profile_scopes(scope_name_list=split_string)

def profile_scope_list_to_str(profile_scopes: list[ProfileScope]) -> str:
    """
    Converts a list of profile scopes to a combined scope string (space separated)

    Args:
        profile_scopes (list[ProfileScope]): The list of profile scopes.

    Returns:
        str: The combined scope string (space separated).
    """
    return " ".join([profile_scope_to_str(scope=scope) for scope in profile_scopes])

def convert_names_to_scopes(scope_names: list[str], client: Client) -> list[ClientScope]:
    """
    Converts a list of scope names to a list of ClientScope objects. 
    
    NOTE: This method assumes that the scope names are valid for the client.

    Args:
        scope_names (list[str]): List of scope names.
        client (Client): The client object that the scopes belong to.

    Returns:
        list[ClientScope]: List of ClientScope objects. None if a scope name does not exist for the client.
    """
    client_scopes: list[ClientScope] = []
    located: bool
    for s_name in scope_names:
        located = False
        for c_scope in client.scopes:
            if s_name == c_scope.name:
                client_scopes.append(c_scope)
                located = True
        if not located: return None
    return client_scopes

def map_attributes_to_access_types(scopes: list[ClientScope], metadata_attributes: bool = None) -> dict[str, list[ScopeAccessType]]:
    """
    Maps the attributes to their access types for a list of client scopes.

    Args:
        scopes (list[ClientScope]): The list of client scopes.
        metadata_attributes (bool): Whether to map the metadata attributes or account attributes. Defaults to None (both).

    Returns:
        dict[str, list[ScopeAccessType]]: The mapping of attributes to their access types.
    """
    mappings: dict[str, list[ScopeAccessType]] = {}
    for scope in scopes:
        if metadata_attributes is None or metadata_attributes is True:
            for attribute in scope.associated_attributes.client_attributes:
                if attribute.attribute_name not in mappings:
                    mappings[attribute.attribute_name] = []
                if attribute.access_type not in mappings[attribute.attribute_name]:
                    mappings[attribute.attribute_name].append(attribute.access_type)
        if metadata_attributes is None or metadata_attributes is False:
            for attribute in scope.associated_attributes.account_attributes:
                if attribute.attribute_name not in mappings:
                    mappings[attribute.attribute_name.value] = []
                if attribute.access_type not in mappings[attribute.attribute_name.value]:
                    mappings[attribute.attribute_name.value].append(attribute.access_type)
    return mappings
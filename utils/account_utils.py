from models.account_models import ProfileScope
from models.client_models import MetadataAttribute


def generate_default_metadata(profile_metadata_attributes: list[MetadataAttribute], 
                              profile_defaults: dict[str, any]) -> dict[str, any]:
    """
    Generate the default metadata for a profile.

    Args:
        profile_metadata_attributes (list[MetadataAttribute]): The metadata attributes that the client can store in the user's profile.
        profile_defaults (dict[str, any]): Any default values that the client wants to store in the user's profile.

    Returns:
        dict[str, any]: The default metadata for the profile.
    """
    new_metadata: dict[str, any] = {metadata.name:None for metadata in profile_metadata_attributes}
    for key, value in profile_defaults.items():
        if key in new_metadata:
            new_metadata[key] = value
    return new_metadata

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
        list[ProfileScope]: The list of profile scopes.
    """
    return [str_to_profile_scope(scope=scope_name) for scope_name in scope_name_list]

def str_to_list_of_profile_scopes(scopes_str_list: str) -> list[ProfileScope]:
    """
    Converts a space seperated list as a string to a list of profile scopes.
    
    NOTE: Assumes that the scopes are valid.

    Args:
        scopes_str_list (str): The space separated list of scope names.

    Returns:
        list[ProfileScope]: The list of profile scopes.
    """
    seperated_scopes: list[str] = scopes_str_list.split(" ")
    return scopes_to_profile_scopes(scope_name_list=seperated_scopes)

def profile_scope_list_to_str(profile_scopes: list[ProfileScope]) -> str:
    """
    Converts a list of profile scopes to a combined scope string (space separated)

    Args:
        profile_scopes (list[ProfileScope]): The list of profile scopes.

    Returns:
        str: The combined scope string (space separated).
    """
    return " ".join([profile_scope_to_str(scope=scope) for scope in profile_scopes])
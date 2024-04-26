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

def scopes_to_profile_scopes(scope_name_list: list[str], client_id: str) -> list[ProfileScope]:
    """
    Converts a list of scope names to a list of profile scopes.
    
    NOTE: Assumes that the scopes are valid and belong to the given client.

    Args:
        scope_name_list (list[str]): The list of scope names.
        client_id (str): The client_id of the application the scopes belong to.

    Returns:
        list[ProfileScope]: The list of profile scopes.
    """
    return [ProfileScope(client_id=client_id, scope=scope_name) for scope_name in scope_name_list]
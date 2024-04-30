from models.account_models import Account, Profile
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

def get_profile_from_account(account: Account, client_id: str) -> Profile:
    """
    Get a profile from an account based on client_id.

    Args:
        client_id (str): The client_id of the application.

    Returns:
        Optional[Profile]: The profile of the user for the given application. None if the profile does not exist.
    """
    for profile in account.profiles:
        if profile.client_id == client_id:
            return profile
    return None

def get_profile_attribute_from_account(account: Account, client_id: str, attribute_name: str) -> any:
    """
    Get a specific attribute from a profile.

    Args:
        account (Account): The account to get the attribute from.
        client_id (str): The client_id of the application the attribute belongs to.
        attribute_name (str): The name of the attribute to get.

    Returns:
        any: The value of the attribute. None if the attribute does not exist.
    """
    profile: Profile = get_profile_from_account(account=account, client_id=client_id)
    if not profile: return None
    return profile.metadata.get(attribute_name)
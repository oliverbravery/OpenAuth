from models.account_models import Account, Profile
from models.client_models import MetadataAttribute
from models.scope_models import AccountAttribute


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

def get_account_attribute(account: Account, attribute: AccountAttribute) -> any:
    """
    Get an attribute from an account. If the attribute does not exist, return None.

    Args:
        account (Account): The account to get the attribute from.
        attribute (AccountAttribute): The attribute to get from the account.

    Returns:
        any: The attribute value if it exists, None otherwise.
    """
    if hasattr(account, attribute.value):
        return getattr(account, attribute.value)
    return None
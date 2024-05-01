from fastapi import HTTPException, status
from models.account_models import Account, AccountRole, Profile
from common import db_manager
from models.auth_models import Authorization
from models.client_models import Client
from models.scope_models import AccountAttribute, ClientScope, ProfileScope, ScopeAccessType
from services.auth_services import get_mapped_client_scopes_from_profile_scopes
from utils.account_utils import generate_default_metadata, get_account_attribute, get_profile_from_account
from validators.account_validators import check_profile_exists, verify_attribute_is_correct_type

def register_account_in_db_collections(new_account: Account) -> int:
    """
    Register a new account in the database collections.
    Adds the new account to the accounts collection and the authorization collection.

    Args:
        new_account (Account): The account to be registered.

    Returns:
        int: 0 if the account was successfully registered, -1 otherwise.
    """
    response: int = db_manager.accounts_interface.add_account(account=new_account)
    if response == -1: return -1
    authorization_object: Authorization = Authorization(username=new_account.username)
    response: int = db_manager.authorization_interface.add_authorization(authorization=authorization_object)
    if response == -1: 
        response: int = db_manager.accounts_interface.delete_account(username=new_account.username)
        return -1
    return 0

def generate_client_profile(client_id: str) -> Profile:
    """
    Generates a new profile based on client metadata and defaults.

    Args:
        client_id (str): The client id of the application.

    Returns:
        Profile: The new profile object.
    """
    client: Client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return None
    default_metadata: dict[str, any] = generate_default_metadata(profile_metadata_attributes=client.profile_metadata_attributes,
                                                                 profile_defaults=client.profile_defaults)
    new_profile: Profile = Profile(
        client_id=client_id,
        metadata=default_metadata
        )
    return new_profile

def create_profile_if_not_exists(client_id: str, username: str) -> int:
    """
    Creates a profile if it does not already exist.
    
    NOTE: If the profile already exists 0 is returned.

    Args:
        client_id (str): Client id of the application.
        username (str): The username of the user.

    Returns:
        int: 0 if the profile was created successfully, -1 if the profile could not be created.
    """
    if check_profile_exists(username=username, client_id=client_id): return 0
    new_profile: Profile = generate_client_profile(client_id=client_id)
    if not new_profile: return -1
    return db_manager.accounts_interface.add_profile_to_account(username=username, profile=new_profile)
    
def enroll_account_as_developer(account: Account) -> int:
    """
    Enrolls a user as a developer.

    Args:
        account (Account): The account to enroll as a developer.

    Returns:
        int: 0 if the account was successfully enrolled as a developer, -1 otherwise.
    """
    account.account_role = AccountRole.DEVELOPER
    return db_manager.accounts_interface.update_account(account=account)

def get_scoped_account_attributes(username: str, scopes: list[ProfileScope], allowed_access_types: list[ScopeAccessType]) -> dict[str, any]:
    """
    Get the attributes of an account based on the scopes.
    
    NOTE: Only attributes for scopes that have a ScopeAccessType from allowed_access_types are returned. Useful for only getting READ attributes for example.

    Args:
        username (str): The username of the account.
        scopes (list[ProfileScope]): The scopes that the client has access to.
        allowed_access_types (list[ScopeAccessType]): The access type of attributes to be returned.

    Returns:
        dict[str, any]: Dictionary of account attributes (Attribute name: Attribute value). Attribute name is composed of client_id and attribute name (<client_id>.<attribute_name>).
    """
    if len(scopes) == 0: return {}
    account: Account = db_manager.accounts_interface.get_account(username=username)
    if not account: return None
    client_id_to_client_scope: dict[str, list[ClientScope]] = get_mapped_client_scopes_from_profile_scopes(profile_scopes=scopes)
    if not client_id_to_client_scope: return None
    attributes: dict[str, any] = {}
    for client_id, client_scopes in client_id_to_client_scope.items():
        for scope in client_scopes:
            for attribute in scope.associated_attributes:
                if attribute.access_type in allowed_access_types:
                    profile: Profile = get_profile_from_account(account=account, client_id=client_id)
                    if not profile: return None
                    fetched_value: any = profile.metadata.get(attribute.attribute_name)
                    attributes[f"{client_id}.{attribute.attribute_name}"] = fetched_value
    return attributes

def get_account_attributes(username: str, attributes: list[AccountAttribute]) -> dict[str, any]:
    """
    Get the account attributes for the given username.

    Args:
        username (str): The username of the account.
        attributes (list[AccountAttribute]): The attributes to get from the account.

    Returns:
        dict[str, any]: Dictionary of account attributes (Attribute name: Attribute value). None if the account does not exist or if an attribute does not exist.
    """
    account: Account = db_manager.accounts_interface.get_account(username=username)
    if not account: return None
    retreived_values: dict[str, any] = {}
    for attribute in attributes:
        retreived_value: any = get_account_attribute(account=account, attribute=attribute)
        if retreived_value is None:
            return None
        retreived_values[attribute.value] = retreived_value
    return retreived_values

def update_existing_attributes(username: str, attribute_updates: dict[str, any]) -> int:
    """
    Update the existing attributes of a profile.
    
    NOTE: Assumes that valid permissions have been checked before calling this function.
    
    Checks:
    - The account exists.
    - The attributes are in the correct format (<client_id>.<attribute_name>), exist in the profile and are of the correct type.
    - The user already has the profiles in their account.
    
    Raises:
    - HTTPException: 404 - Account not found.
    - HTTPException: 400 - Attribute name is not in the correct format.
    - HTTPException: 404 - Account does not have an profile assosiated with the requested update attributes.
    - HTTPException: 400 - Attribute does not exist in the profile.

    Args:
        username (str): The username of the account.
        attribute_updates (dict[str, any]): The attributes to update. The key is the combined attribute name (<client_id>.<attribute_name>) and the value is the new value.

    Returns:
        int: 0 if the attributes were updated successfully, -1 otherwise.
    """
    account: Account = db_manager.accounts_interface.get_account(username=username)
    if not account: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")
    client_id_to_local_attribute_updates: dict[str, dict[str, any]] = {}
    for attribute, new_value in attribute_updates.items():
        split_attribute: list[str] = attribute.split('.')
        if len(split_attribute) != 2: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attribute name is not in the correct format.")
        client_id, attribute_name = split_attribute[0], split_attribute[1]
        if client_id not in client_id_to_local_attribute_updates:
            client_id_to_local_attribute_updates[client_id] = {}
        client_id_to_local_attribute_updates[client_id][attribute_name] = new_value
    for client_id, local_attribute_updates in client_id_to_local_attribute_updates.items():
        profile: Profile = get_profile_from_account(account=account, client_id=client_id)
        if not profile: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account does not have an profile assosiated with the requested update attributes.")
        client: Client = db_manager.clients_interface.get_client(client_id=client_id)
        if not client: return -1
        for attribute_name, attribute_value in local_attribute_updates.items():
            if not verify_attribute_is_correct_type(client=client, attribute_name=attribute_name, value=attribute_value): return -1
            if attribute_name not in profile.metadata: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attribute does not exist in the profile.")
            profile.metadata[attribute_name] = attribute_value
        response: int = db_manager.accounts_interface.update_profile(username=username, profile=profile)
        if response == -1: return -1
    return 0
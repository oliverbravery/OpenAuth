from models.account_models import Account, AccountRole, Profile
from common import db_manager
from models.auth_models import Authorization
from models.client_models import Client
from models.scope_models import ClientScope, ProfileScope, ScopeAccessType
from services.auth_services import get_mapped_client_scopes_from_profile_scopes
from utils.account_utils import generate_default_metadata, get_profile_attribute_from_account
from utils.scope_utils import scopes_to_profile_scopes
from validators.account_validators import check_profile_exists

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

def generate_client_profile(client_id: str, scopes: str) -> Profile:
    """
    Generates a new profile based on client metadata and defaults.

    Args:
        client_id (str): The client id of the application.
        scopes (str): The accepted scopes requested by the client.

    Returns:
        Profile: The new profile object.
    """
    client: Client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return None
    default_metadata: dict[str, any] = generate_default_metadata(profile_metadata_attributes=client.profile_metadata_attributes,
                                                                 profile_defaults=client.profile_defaults)
    scopes_as_list: list[str] = scopes.split(" ")
    if scopes_as_list == ['']: scopes_as_list = []
    new_profile: Profile = Profile(
        client_id=client_id,
        scopes=scopes_to_profile_scopes(scope_name_list=scopes_as_list),
        metadata=default_metadata
        )
    return new_profile

def create_profile_if_not_exists(client_id: str, username: str, accecpted_scopes: str) -> int:
    """
    Creates a profile if it does not already exist.
    
    NOTE: If the profile already exists, the accepted scopes are updated regardless.

    Args:
        client_id (str): Client id of the application.
        username (str): The username of the user.
        accecpted_scopes (str): The accepted scopes requested by the client.

    Returns:
        int: 0 if the profile was created successfully, -1 if the profile could not be created.
    """
    if check_profile_exists(username=username, client_id=client_id):  
        response: int = db_manager.accounts_interface.update_profile_scopes(username=username, 
                                                                            client_id=client_id, 
                                                                            scopes=accecpted_scopes)
        return response
    new_profile: Profile = generate_client_profile(client_id=client_id, scopes=accecpted_scopes)
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
                    fetched_value: any = get_profile_attribute_from_account(account=account, 
                                                                            client_id=client_id, 
                                                                            attribute_name=attribute.attribute_name)
                    if fetched_value is None: return None
                    attributes[f"{client_id}.{attribute.attribute_name}"] = fetched_value
    return attributes
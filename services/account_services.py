from models.account_models import Account, AccountRole, Profile
from common import db_manager
from models.auth_models import Authorization
from models.client_models import Client, MetadataAttribute
from models.util_models import ConcentDetails
from utils.account_utils import generate_default_metadata
from validators.user_validators import check_profile_exists

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
    new_profile: Profile = Profile(
        client_id=client_id,
        scopes=scopes_as_list,
        metadata=default_metadata
        )
    return new_profile

def create_profile_if_not_exists(client_id: str, username: str, accecpted_scopes: str) -> int:
    """
    Creates a profile if it does not already exist.

    Args:
        client_id (str): Client id of the application.
        username (str): The username of the user.
        accecpted_scopes (str): The accepted scopes requested by the client.

    Returns:
        int: 0 if the profile was created successfully, -1 if the profile could not be created.
    """
    if check_profile_exists(username=username, client_id=client_id): return 0
    new_profile: Profile = generate_client_profile(client_id=client_id, scopes=accecpted_scopes)
    if not new_profile: return -1
    return db_manager.accounts_interface.add_profile_to_account(username=username, profile=new_profile)
    
def get_client_concent_details(client_id: str, scopes: list[str]) -> ConcentDetails:
    """
    Fetches the details from the client required for the consent form.

    Args:
        client_id (str): The client id of the application.
        scopes (list[str]): The scopes requested by the client.

    Returns:
        ConcentDetails: A model containing the details required for the consent form.
    """
    client: Client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return None
    return ConcentDetails(name=client.name, 
                          description=client.description, 
                          scopes_description=client.scopes,
                          client_redirect_uri=client.redirect_uri)
    
def enroll_account_as_developer(account: Account) -> int:
    """
    Enrolls a user as a developer.

    Args:
        account (Account): The account to enroll as a developer.

    Returns:
        int: 0 if the account was successfully enrolled as a developer, -1 otherwise.
    """
    account.account_role = AccountRole.DEVELOPER
    return db_manager.accounts_interface.update_generic(account)
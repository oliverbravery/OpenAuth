from models.account_models import Account, AccountRole
from models.client_models import Client, MetadataType
from datetime import datetime
from common import db_manager
from utils.hash_utils import verify_hash

def validate_client_credentials(client_id: str, client_secret: str) -> bool:
    """
    Validate the client credentials.

    Args:
        client_id (str): The client id of the application.
        client_secret (str): The client secret of the application.

    Returns:
        bool: True if the client credentials are valid, False otherwise.
    """
    client: Client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return False
    return verify_hash(plaintext=client_secret, urlsafe_hash=client.client_secret_hash)

def validate_client_developers(client: Client) -> bool:
    """
    Validate that the client's developers exist as developer accounts and that their scopes are developer only scopes in their client.
    
    NOTE: 
    - This function returns False if the scopes are not associated with the specified client.
    - Scopes in the ClientDeveloper are assumed to be of the same client so are NOT in the <client_id>:<scope> format.
    
    Args:
        client (Client): The client to validate.

    Returns:
        bool: True if the client developers are valid, False otherwise.
    """
    client_developer_scope_names: list[str] = [scope.name for scope in client.scopes if scope.developer_only]
    for developer in client.developers:
        developer_account: Account = db_manager.accounts_interface.get_account(username=developer.username)
        if not developer_account or developer_account.account_role != AccountRole.DEVELOPER: return False
        for dev_scope in developer.scopes:
            if dev_scope not in client_developer_scope_names: return False
    return True

def validate_metadata_attributes(client: Client) -> bool:
    """
    Validate that the metadata attributes have unique names.
    
    Args:
        client (Client): The client to validate.

    Returns:
        bool: True if the metadata attributes are valid, False otherwise.
    """
    metadata_attribute_names: list[str] = [metadata_attribute.name for metadata_attribute in client.profile_metadata_attributes]
    return len(metadata_attribute_names) == len(set(metadata_attribute_names))

def validate_attribute_for_metadata_type(metadata_type: type, value: any) -> bool:
    """
    Validate that the value is of the correct type for the metadata attribute.

    Args:
        metadata_type (type): The type of the metadata attribute.
        value (any): The value to validate.

    Returns:
        bool: True if the value is of the correct type, False otherwise.
    """
    match metadata_type:
        case datetime.datetime:
            try:
                _ = datetime.fromisoformat(value)
                return True
            except Exception:
                return False
        case _:
            return isinstance(value, metadata_type)

def validate_profile_defaults(client: Client) -> bool:
    """
    Check that the profile defaults are valid for the metadata attributes.

    Checks the profile defaults exist as metadata attributes and the specified defaults are of the correct type.

    Args:
        client (Client): The client to validate.

    Returns:
        bool: True if the profile defaults are valid, False otherwise.
    """
    all_mapped_attributes: dict[str, MetadataType] = {metadata_attribute.name: metadata_attribute.type for metadata_attribute in client.profile_metadata_attributes}
    for key, value in client.profile_defaults.items():
        if key not in all_mapped_attributes: return False
        valid_datatype: type = all_mapped_attributes[key].get_pythonic_type()
        if not validate_attribute_for_metadata_type(metadata_type=valid_datatype, value=value): return False
    return True
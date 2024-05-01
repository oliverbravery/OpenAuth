from fastapi import HTTPException, status
from common import db_manager
from models.account_models import Account, AccountRole
from models.client_models import Client
from utils.account_utils import get_profile_from_account
from utils.password_manager import PasswordManager
from validators.client_validators import validate_attribute_for_metadata_type

def check_user_exists(username: str) -> bool:
    """
    Check if a user exists in the database.

    Args:
        username (str): The username of the user.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    return bool(db_manager.accounts_interface.get_account(username=username))

def validate_user_credentials(username: str, password: str) -> int:
    """
    Validate the user credentials.

    Args:
        username (str): The username of the user.
        password (str): The plaintext password of the user.

    Returns:
        int: 0 if the user credentials are valid, -1 otherwise.
    """
    account: Account = db_manager.accounts_interface.get_account(username=username)
    if not account: return -1
    if not PasswordManager.verify_password(plain_password=password, 
                                           hashed_password=account.hashed_password): return -1
    return 0

def verify_account_is_developer(account: Account) -> bool:
    """
    Checks if an account is a developer account.
    Raises an HTTPException if the account is not a developer account.
    
    Args:
        account (Account): The account to check.
    
    Returns:
        bool: True if the account is a developer account, False otherwise.
    """
    if account.account_role != AccountRole.DEVELOPER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="This account is not a developer account.")
    return True

def check_profile_exists(username: str, client_id: str) -> bool:
    """
    Check if a profile exists in the database.

    Args:
        username (str): The username of the profile.

    Returns:
        bool: True if the profile exists, False otherwise.
    """
    account: Account = db_manager.accounts_interface.get_account(username=username)
    if not account: return False
    return True if get_profile_from_account(account=account, 
                                            client_id=client_id) else False
    
def verify_attribute_is_correct_type(client: Client, attribute_name: str, value: any) -> bool:
    """
    Check that the attribute value is of the correct type for the metadata attribute.

    Args:
        client (Client): The client to check.
        attribute_name (str): The name of the attribute.
        value (any): The value to check.

    Returns:
        bool: True if the attribute value is of the correct type, False otherwise.
    """
    
    for metadata_attribute in client.profile_metadata_attributes:
        if metadata_attribute.name == attribute_name:
            return validate_attribute_for_metadata_type(metadata_type=metadata_attribute.type.get_pythonic_type(),
                                                 value=value)
    return False
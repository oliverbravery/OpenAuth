from fastapi import HTTPException, status
from common import db_manager
from models.account_models import Account, AccountRole
from utils.password_manager import PasswordManager

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

def check_account_is_developer(account: Account) -> bool:
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
        return False
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
    return True if account.get_profile(client_id=client_id) else False
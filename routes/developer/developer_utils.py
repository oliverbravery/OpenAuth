from main import db_manager
from database.models import Account, AccountRole
from fastapi import HTTPException, status

def enroll_user_as_developer(account: Account) -> int:
    """
    Enrolls a user as a developer.

    Args:
        account (Account): The account to enroll as a developer.

    Returns:
        int: 0 if the account was successfully enrolled as a developer, -1 otherwise.
    """
    account.account_role = AccountRole.DEVELOPER
    return db_manager.accounts_interface.update_generic(account)

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
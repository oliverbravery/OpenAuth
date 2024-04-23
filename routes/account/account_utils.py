from base64 import urlsafe_b64encode
import hashlib
from secrets import token_urlsafe
from main import db_manager
from database.models import Account, Authorization

def check_user_exists(username: str) -> bool:
    """
    Check if a user exists in the database.

    Args:
        username (str): The username of the user.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    return bool(db_manager.accounts_interface.get_account(username=username))

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

def generate_code_challenge_and_verifier() -> tuple[str, str]:
    """
    Generate a code challenge and code verifier for PKCE.

    Returns:
        tuple[str, str]: The code challenge and code verifier as a tuple (code_challenge, code_verifier).
    """
    code_verifier: str = token_urlsafe(256)
    code_challenge: str = urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode()
    return code_challenge, code_verifier
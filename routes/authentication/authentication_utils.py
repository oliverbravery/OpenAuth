from main import db_manager
from database.models import Account
from routes.authentication.password_manager import PasswordManager
from secrets import token_urlsafe
import os
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode, urlsafe_b64decode

fernet: Fernet = Fernet(os.getenv("AUTH_CODE_SECRET"))

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

def generate_authorization_code(username: str) -> str:
    """
    Generate an encrypted authorization code with a username.
        
    Args:
        username (str): The username of the user to be authorized.

    Returns:
        str: The generated URL safe authorization code.
    """
    auth_code: str = token_urlsafe(32)
    combined_code: str = f"{username}:{auth_code}"
    encrypted_code: bytes = fernet.encrypt(combined_code.encode())
    encrypted_code_urlsafe: bytes = urlsafe_b64encode(encrypted_code)
    encrypted_code_str: str = encrypted_code_urlsafe.decode('ascii')
    return  encrypted_code_str

def decrypt_authorization_code(auth_code: str) -> tuple[str, str]:
    """
    Decrypt an encrypted authorization code.

    Args:
        auth_code (str): The encrypted authorization code.
        
    Returns:
        tuple[str, str]: The username and the authorization code.
    """
    encrypted_code_urlsafe: bytes = auth_code.encode('ascii')
    encrypted_code: bytes = urlsafe_b64decode(encrypted_code_urlsafe)
    combined_code: bytes = fernet.decrypt(encrypted_code)
    combined_code_str: str = combined_code.decode()
    return combined_code_str.split(":")[0], combined_code_str[len(combined_code_str.split(":")[0])+1:]

def get_access_token_with_authorization_code():
    pass

def get_access_token_with_refresh_token():
    pass
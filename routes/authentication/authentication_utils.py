from main import db_manager
from database.models import Account
from routes.authentication.password_manager import PasswordManager
from secrets import token_urlsafe
import os
from cryptography.fernet import Fernet

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
    Generate an authorization code of 32 bytes (256bits), appends the username to the code and encrypts it using a secret key.
    
    Args:
        username (str): The username of the user to be authorized.

    Returns:
        str: The generated authorization code.
    """
    auth_code: str = token_urlsafe(32)
    combined_code: str = f"{username}:{auth_code}"
    encrpyted_code: bytes = fernet.encrypt(combined_code.encode())
    return  encrpyted_code

def decrypt_authorization_code(auth_code: str) -> tuple[str, str]:
    """
    Decrypt an authorization code using a secret key.

    Args:
        auth_code (str): The encrypted authorization code.
        
    Returns:
        tuple[str, str]: The username and the authorization code.
    """
    decrypted_code: str = fernet.decrypt(auth_code.encode()).decode()
    return decrypted_code.split(":")[0], decrypted_code[len(decrypted_code.split(":")[0])+1:]
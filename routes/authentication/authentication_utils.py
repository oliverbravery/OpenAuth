from main import db_manager
from database.models import Account, Authorization
from routes.authentication.password_manager import PasswordManager
from routes.authentication.token_manager import TokenManager
from routes.authentication.models import TokenType, TokenResponse
from secrets import token_urlsafe
import os
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode, urlsafe_b64decode
import hashlib
import bcrypt

fernet: Fernet = Fernet(os.getenv("AUTH_CODE_SECRET"))

token_manager: TokenManager = TokenManager(
    access_token_expire_time=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")),
    refresh_token_expire_time=int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")),
    secret_key=str(os.getenv("TOKEN_SIGNING_KEY")),
    token_algorithm=str(os.getenv("TOKEN_ALGORITHM"))
)

def verify_hash(plaintext: str, urlsafe_hash: str) -> bool:
    """
    Verifies a plaintext string against a URL safe hash.

    Args:
        plaintext (str): Plaintext string to be verified.
        urlsafe_hash (str): URL safe hash to be verified against.

    Returns:
        bool: True if the plaintext string matches the URL safe hash, False otherwise.
    """
    hashed_bytes: bytes = urlsafe_b64decode(urlsafe_hash.encode('utf-8'))
    return bcrypt.checkpw(plaintext.encode('utf-8'), hashed_bytes)

def hash_string(plaintext: str) -> str:
    """
    Hash a plaintext string using bcrypt and return the URL safe hash.

    Args:
        plaintext (str): Plaintext string to be hashed.

    Returns:
        str: URL safe hash of the plaintext string.
    """
    hashed_bytes: bytes = bcrypt.hashpw(plaintext.encode('utf-8'), bcrypt.gensalt())
    urlsafe_hash: str = urlsafe_b64encode(hashed_bytes).decode('utf-8')
    return urlsafe_hash

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
    encrypted_code_str: str = encrypted_code_urlsafe.decode()
    return  encrypted_code_str

def decrypt_authorization_code(auth_code: str) -> tuple[str, str]:
    """
    Decrypt an encrypted authorization code.

    Args:
        auth_code (str): The encrypted authorization code.
        
    Returns:
        tuple[str, str]: The username and the authorization code as a tuple (username, auth_code).
    """
    encrypted_code_urlsafe: bytes = auth_code.encode()
    encrypted_code: bytes = urlsafe_b64decode(encrypted_code_urlsafe)
    combined_code: bytes = fernet.decrypt(encrypted_code)
    combined_code_str: str = combined_code.decode()
    return combined_code_str.split(":")[0], combined_code_str[len(combined_code_str.split(":")[0])+1:]

def verify_authorization_code(auth_code: str, username: str) -> bool:
    """
    Verify an authorization code.

    Args:
        auth_code (str): The authorization code.
        username: (str): The username of the user to be authorized.
        
    Returns:
        bool: True if the authorization code is valid, False otherwise.
    """
    authorization: Authorization = db_manager.authorization_interface.get_authorization(username=username)
    if not authorization: return False
    return authorization.auth_code == auth_code

def verify_code_challenge(code_challenge: str, code_verifier: str) -> bool:
    """
    Verify a code challenge using SHA-256.

    Args:
        code_challenge (str): The code challenge.
        code_verifier (str): The code verifier.
        
    Returns:
        bool: True if the code challenge is valid, False otherwise.
    """
    generated_code_challenge: str = urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode()
    return code_challenge == generated_code_challenge


def get_tokens_with_authorization_code(auth_code: str, code_verifier: str, client_id: str) -> TokenResponse:
    """
    Get access and refresh tokens and store the refresh token in the database. 
    Also, remove the authorization code and code challenge from the database after use.

    Args:
        auth_code (str): Encrypted authenticaion code to be used to get the tokens.
        code_verifier (str): Code verifier used to verify the code challenge.
        client_id (str): The client id of the application requesting the tokens.

    Returns:
        TokenResponse: OAuth2.0 compliant token response.
    """
    username, decoded_authorization_code = decrypt_authorization_code(auth_code=auth_code)
    if not verify_authorization_code(auth_code=decoded_authorization_code, username=username): return None
    authorization: Authorization = db_manager.authorization_interface.get_authorization(username=username)
    if not authorization or not authorization.code_challenge: return None
    if not verify_code_challenge(code_challenge=authorization.code_challenge, code_verifier=code_verifier): return None
    authorization.code_challenge = None
    authorization.auth_code = None
    user_account: Account = db_manager.accounts_interface.get_account(username=username)
    if not user_account: return None
    access_token: str = token_manager.generate_and_sign_jwt_token(tokenType=TokenType.ACCESS,
                                                                  account=user_account,
                                                                  client_id=client_id)
    refresh_token: str = token_manager.generate_and_sign_jwt_token(tokenType=TokenType.REFRESH,
                                                                   account=user_account,
                                                                   client_id=client_id)
    if not access_token or not refresh_token: return None
    authorization.hashed_refresh_token = hash_string(plaintext=refresh_token)
    response: int = db_manager.authorization_interface.update_authorization(authorization)
    if response == -1: return None
    access_token_expires_in_seconds: int = token_manager.get_token_expire_time(token_type=TokenType.ACCESS)*60
    token_response: TokenResponse = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_token_expires_in_seconds
    )
    return token_response

def get_tokens_with_refresh_token():
    # TODO: Ensuure only client (x) can request and gain access to certain profiles (using client_secret)
    pass
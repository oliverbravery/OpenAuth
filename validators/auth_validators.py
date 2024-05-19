from base64 import urlsafe_b64encode
import hashlib
from utils.token_manager import TokenManager
from utils.hash_utils import verify_hash
from models.token_models import BaseToken, StateToken, TokenType
from models.auth_models import Authorization
from common import db_manager, token_manager, config

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

def login_state_valid(login_state: str, username: str, scopes: str) -> bool:
    """
    Checks that the login state is signed correctly and has not expired. 

    Args:
        login_state (str): The StateToken to validate.
        username (str): The username to cross reference with the login state.
        scopes (str): The scopes to cross reference with the login state.

    Returns:
        bool: True if the login state is valid. False if not.
    """
    if not config.dev_config.login_state_validation_enabled: return True
    token: StateToken = token_manager.decode_jwt_token(token=login_state, token_type=TokenType.STATE)
    if token is None: return False
    if token.sub != username: return False
    if token.scope != scopes: return False
    return True

def verify_auth_token_hash(token: BaseToken, token_type: TokenType) -> bool:
    """
    Check if the token is valid in the database. If null in database the token is valid.

    Args:
        token (BaseToken): The token to validate.
        token_type (TokenType): The type of the token.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    plaintext: str = TokenManager.get_token_hashable_string(token=token)
    authorization: Authorization = db_manager.authorization_interface.get_authorization(username=token.sub)
    ciphertext: str = None
    if not authorization: return False
    if token_type == TokenType.ACCESS:
        ciphertext = authorization.hashed_access_token
    elif token_type == TokenType.REFRESH:
        ciphertext = authorization.hashed_refresh_token
    if ciphertext is None: return True
    return verify_hash(plaintext=plaintext, urlsafe_hash=ciphertext)
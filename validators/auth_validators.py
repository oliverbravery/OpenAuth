from base64 import urlsafe_b64encode
import hashlib
from models.token_models import StateToken, TokenType
from models.auth_models import Authorization
from common import db_manager, token_manager

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
    token: StateToken = token_manager.decode_jwt_token(token=login_state, token_type=TokenType.STATE)
    if token is None: return False
    if token.sub != username: return False
    if token.scope != scopes: return False
    return True
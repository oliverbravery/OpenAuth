from main import db_manager
from database.models import Account, Authorization, Client
from routes.authentication.password_manager import PasswordManager
from routes.authentication.token_manager import TokenManager
from routes.authentication.models import TokenType, TokenResponse, RefreshToken, AccessToken, AuthorizeResponse, ConcentDetails
from secrets import token_urlsafe
import os
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode, urlsafe_b64decode
import hashlib
import bcrypt
from fastapi import HTTPException, status
from starlette.requests import Request
import requests
from requests import Response
from starlette.formparsers import FormData
from pydantic import BaseModel

fernet: Fernet = Fernet(os.getenv("AUTH_CODE_SECRET"))

recaptcha_secret_key: str = os.getenv("RECAPTCHA_SECRET_KEY")
if not recaptcha_secret_key: raise ValueError("RECAPTCHA_SECRET_KEY not set in environment variables.")
google_verify_url: str = f"https://www.google.com/recaptcha/api/siteverify?secret={recaptcha_secret_key}&response="

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

def generate_authorization_code(username: str) -> tuple[str, str]:
    """
    Generate an encrypted authorization code with a username.
        
    Args:
        username (str): The username of the user to be authorized.

    Returns:
        tuple[str, str]: The generated URL safe encrypted authorization code and the plaintext authorization code (encrypted auth code, auth_code).
    """
    auth_code: str = token_urlsafe(32)
    combined_code: str = f"{username}:{auth_code}"
    encrypted_code: bytes = fernet.encrypt(combined_code.encode())
    url_safe: str = urlsafe_b64encode(encrypted_code).decode()
    return url_safe, auth_code

def decrypt_authorization_code(auth_code: str) -> tuple[str, str]:
    """
    Decrypt an encrypted authorization code.

    Args:
        auth_code (str): The encrypted authorization code.
        
    Returns:
        tuple[str, str]: The username and the authorization code as a tuple (username, auth_code).
    """
    decrypted_combined_code: str = fernet.decrypt(urlsafe_b64decode(auth_code.encode())).decode()
    return decrypted_combined_code.split(":")[0], decrypted_combined_code[len(decrypted_combined_code.split(":")[0])+1:]

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
    return client.client_secret == client_secret

def generate_and_store_tokens(authorization: Authorization, user_account: Account, client_id: str) -> TokenResponse:
    """
    Generate access and refresh tokens and store the refresh token hash in the database.

    Args:
        authorization (Authorization): The authorization object related to the user.
        user_account (Account): The account object of the user.
        client_id (str): The client id of the application requesting the tokens.

    Returns:
        TokenResponse: OAuth2.0 compliant token response.
    """
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

def get_tokens_with_authorization_code(auth_code: str, code_verifier: str, client_id: str, client_secret: str) -> TokenResponse:
    """
    Get access and refresh tokens and store the refresh token in the database. 
    Remove the authorization code and code challenge from the database after use.
    
    NOTE: This function also checks that the code challenge is valid, using the code verifier.

    Args:
        auth_code (str): Encrypted authenticaion code to be used to get the tokens.
        code_verifier (str): Code verifier used to verify the code challenge.
        client_id (str): The client id of the application requesting the tokens.
        client_secret (str): The client secret of the application requesting the tokens.

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
    if not validate_client_credentials(client_id=client_id, client_secret=client_secret): return None
    return generate_and_store_tokens(authorization=authorization, user_account=user_account, client_id=client_id)

def invalidate_refresh_token(username: str) -> bool:
    """
    Invalidate the refresh token of a user.

    Args:
        username (str): The username of the user whose refresh token is to be invalidated.

    Returns:
        bool: True if the refresh token is invalidated, False otherwise.
    """
    authorization: Authorization = db_manager.authorization_interface.get_authorization(username=username)
    if not authorization: return False
    authorization.hashed_refresh_token = None
    response: int = db_manager.authorization_interface.update_authorization(authorization)
    return response != -1

def get_tokens_with_refresh_token(refresh_token: str) -> TokenResponse:
    """
    Get access and refresh tokens using the refresh token.
    Complies with the OAuth2.0 standard and refresh token rotation flow.

    Args:
        refresh_token (str): The signed refresh token to be used to get the new tokens.

    Returns:
        TokenResponse: The OAuth2.0 complient response object for the /token endpoint.
    """
    decoded_token: RefreshToken = token_manager.verify_and_decode_jwt_token(token=refresh_token, 
                                                                 token_type=TokenType.REFRESH)
    if not decoded_token: return None
    authorization: Authorization = db_manager.authorization_interface.get_authorization(
        username=decoded_token.sub)
    if not authorization: return None
    hashed_refresh_token: str = authorization.hashed_refresh_token
    if not hashed_refresh_token: return None
    if not verify_hash(plaintext=refresh_token, urlsafe_hash=hashed_refresh_token): 
        invalidate_refresh_token(username=decoded_token.sub)
        return None
    if len(decoded_token.aud) != 1: return None
    user_account: Account = db_manager.accounts_interface.get_account(username=decoded_token.sub)
    if not user_account: return None
    return generate_and_store_tokens(authorization=authorization, user_account=user_account, client_id=decoded_token.aud[0])

def generate_and_store_auth_code(state: str, username: str, code_challenge: str) -> AuthorizeResponse:
    """
    Generate an authorization code and store it in the database with the provided state, username, and code challenge.

    Args:
        state (str): The CSRF state.
        username (str): The username of the user.
        code_challenge (str): The code challenge for the authorization code provided by the client.s

    Returns:
        AuthorizeResponse: The response containing the authorization code and CSRF state.
    """
    encrypted_auth_code, authorization_code = generate_authorization_code(username=username)
    csrf_state: str = state
    user_authorization: Authorization = Authorization(
        username=username,
        auth_code=authorization_code,
        code_challenge=code_challenge,
        hashed_refresh_token=None
    )
    response: int = db_manager.authorization_interface.update_authorization(authorization=user_authorization)
    if response == -1: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Authorization failed.")
    return AuthorizeResponse(authorization_code=encrypted_auth_code, state=csrf_state)

def get_client_concent_details(client_id: str, scopes: list[str]) -> ConcentDetails:
    """
    Fetches the details from the client required for the consent form.

    Args:
        client_id (str): The client id of the application.
        scopes (list[str]): The scopes requested by the client.

    Returns:
        ConcentDetails: A model containing the details required for the consent form.
    """
    client: Client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return None
    return ConcentDetails(name=client.name, 
                          description=client.description, 
                          scopes_description=client.scopes,
                          client_redirect_uri=client.redirect_uri)

def configure_redirect_uri(base_uri: str, query_parameters: dict[str, str]) -> str:
    """
    Configure the redirect uri with the query parameters.

    Args:
        base_uri (str): The base uri of the redirect.
        query_parameters (dict[str, str]): The query parameters to be added to the redirect uri.

    Returns:
        str: The complete redirect uri with the query parameters.
    """
    complete_uri: str = base_uri + "?"
    for key, value in query_parameters.items():
        complete_uri += f"{key}={value}&"
    return complete_uri

def valid_client_credentials(client_id: str, client_secret: str) -> bool:
    """
    Validate the client credentials.xw

    Args:
        client_id (str): Client id of the application.
        client_secret (str): Client secret of the application.

    Returns:
        bool: True if the client credentials are valid, False otherwise.
    """
    client: Client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return False
    return client.client_secret == client_secret

def valid_client_scopes(client_id: str, scopes: list[str]) -> bool:
    """
    Check that the client has the requested scopes.

    Args:
        client_id (str): Client id of the application.
        scopes (list[str]): List of scopes requested by the client.

    Returns:
        bool: True if the client scopes are valid, False otherwise.
    """
    client: Client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return False
    client_scopes: list[str] = list(client.scopes.keys())
    return all(scope in client_scopes for scope in scopes)

def verify_captcha_completed(captcha_response: str) -> bool:
    """
    Verify that the captcha was completed.

    Args:
        captcha_response (str): The response from the captcha.

    Returns:
        bool: True if the captcha was completed, False otherwise.
    """
    
    url: str = google_verify_url + captcha_response
    response: Response = requests.request("GET",
                                          url)
    if response.status_code != 200: return False
    if response.json()["success"]: return True
    return False

def form_to_object(form_data: FormData, object_class: BaseModel) -> object:
    """
    Convert form data to a Pydantic object.

    Args:
        form_data (FormData): The form data to be converted.
        object_class (BaseModel): The Pydantic object class to convert the form data to.

    Returns:
        object: The Pydantic object with the form data.
    """
    form_data_dict: dict = {}
    for key, value in form_data.items():
        form_data_dict[key] = value
    return object_class.model_construct(**form_data_dict)

class BearerTokenAuth:
    """
    A class used to authenticate a user using a Bearer token.
    """
    token_prefix: str
    
    def __init__(self, token_prefix: str = "Bearer"):
        """
        The constructor for the BearerTokenAuth class.

        Args:
            token_prefix (str, optional): The prefix for the Bearer token. Defaults to "Bearer".
        """
        self.token_prefix = token_prefix
        
    def abstract_token_from_header(self, auth_header: str | None) -> str:
        """
        Abstracts the token from the Authorization header.

        Args:
            auth_header (str | None): The Authorization header as a string.

        Returns:
            str: The token as a string. None if the token is invalid or not present.
        """
        if not auth_header: return None
        split_auth_header: list[str] = auth_header.split(" ")
        if not len(split_auth_header) == 2: return None
        if not split_auth_header[0] == self.token_prefix: return None
        return split_auth_header[1]
    
    def raise_invalid_token_error(self) -> None:
        """
        Raises an HTTPException with status code 401 and a message indicating an invalid token.
        """
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail=f"Invalid {self.token_prefix} token")
    
    async def __call__(self, request: Request) -> Account:
        """
        Callable method to authenticate the user using the access Bearer token.
        Use as an endpoint parameter to obtain the account of the user assosiated with the token.
        Raises an HTTPException if the token is invalid.
        
        Example:
        ```python
        from fastapi import Depends, FastAPI
        from routes.authentication.authentication_utils import BearerTokenAuth
        app = FastAPI()
        bearer_token_auth: BearerTokenAuth = BearerTokenAuth()
        @app.get("/protected")
        async def protected_endpoint(token: Account = Depends(bearer_token_auth)):
            pass
        ```

        Args:
            request (Request): Used to get the headers from the request.

        Returns:
            Account: The account object of the user associated with the token. Raises an HTTPException if the token is invalid.
        """
        auth_header = request.headers.get("Authorization")
        token: str = self.abstract_token_from_header(auth_header=auth_header)
        if not token: self.raise_invalid_token_error()
        decoded_token: AccessToken = token_manager.verify_and_decode_jwt_token(token=token, token_type=TokenType.ACCESS)
        if not decoded_token: self.raise_invalid_token_error()
        account: Account = db_manager.accounts_interface.get_account(username=decoded_token.sub)
        if not account: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            detail="Issue fetching account information")
        return account
        
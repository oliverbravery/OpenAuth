from fastapi import HTTPException, Request, status
from models.account_models import Account
from models.auth_models import Authorization
from models.client_models import Client
from models.response_models import AuthorizeResponse, TokenResponse
from models.scope_models import ProfileScope
from models.token_models import AccessToken, RefreshToken, TokenType
from models.util_models import ConsentDetails
from utils.auth_utils import decrypt_authorization_code, generate_authorization_code
from utils.hash_utils import hash_string, verify_hash
from common import db_manager, token_manager
from validators.auth_validators import verify_authorization_code, verify_code_challenge
from validators.client_validators import validate_client_credentials


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
    # TODO: access token not generating as there is no profile in the account object for the client id. 
    # TODO: Need to, after consent screen, add the profile to the account object if it's not already there.
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

def refresh_and_update_tokens(refresh_token: str) -> TokenResponse:
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
    
def get_consent_details(client_id: str, requested_scopes: list[ProfileScope]) -> ConsentDetails:
    """
    Fetch and configure the consent details for the consent form.
    
    NOTE: Assumes the requested scopes are valid.

    Args:
        client_id (str): The client id of the application requesting the consent.
        requested_scopes (list[ProfileScope]): The scopes requested by the client.

    Returns:
        ConsentDetails: A model containing the details required for the consent form.
    """
    client: Client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return None
    consent_details: ConsentDetails = ConsentDetails(name=client.name, 
                                                     description=client.description, 
                                                     requested_scopes=requested_scopes, 
                                                     client_redirect_uri=client.redirect_uri)
    return consent_details
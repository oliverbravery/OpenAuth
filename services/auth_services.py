from fastapi import HTTPException, status
from utils.hash_utils import hash_string
from utils.token_manager import TokenManager
from models.account_models import Account
from models.auth_models import Authorization
from models.client_models import Client
from models.response_models import AuthorizeResponse, TokenResponse
from models.scope_models import ClientScope, ProfileScope, ScopeAccessType
from models.token_models import RefreshToken, TokenType
from models.util_models import ConsentDetails
from utils.auth_utils import decrypt_authorization_code, generate_authorization_code
from common import db_manager, token_manager
from utils.scope_utils import map_attributes_to_access_types
from validators.account_validators import check_profile_exists
from validators.auth_validators import verify_authorization_code, verify_code_challenge, verify_token_hash
from validators.client_validators import validate_client_credentials


def generate_and_store_tokens(authorization: Authorization, user_account: Account, client_id: str,
                              scopes: str) -> TokenResponse:
    """
    Generate access and refresh tokens and store the token hashes in the database.

    Args:
        authorization (Authorization): The authorization object related to the user.
        user_account (Account): The account object of the user.
        client_id (str): The client id of the application requesting the tokens.
        scopes (str): space seperated list of scopes as a string.

    Returns:
        TokenResponse: OAuth2.0 compliant token response.
    """
    
    access_token_str, access_token = token_manager.generate_and_sign_jwt_token(tokenType=TokenType.ACCESS,
                                                                  account=user_account,
                                                                  client_id=client_id,
                                                                  scopes=scopes)
    refresh_token_str, refresh_token = token_manager.generate_and_sign_jwt_token(tokenType=TokenType.REFRESH,
                                                                   account=user_account,
                                                                   client_id=client_id,
                                                                   scopes=None)
    if not access_token_str or not refresh_token_str: return None
    authorization.hashed_refresh_token = TokenManager.get_token_hash(token=refresh_token)
    authorization.hashed_access_token = TokenManager.get_token_hash(token=access_token)
    response: int = db_manager.authorization_interface.update_authorization(authorization)
    if response == -1: return None
    access_token_expires_in_seconds: int = token_manager.get_token_expire_time(token_type=TokenType.ACCESS)*60
    token_response: TokenResponse = TokenResponse(
        access_token=access_token_str,
        refresh_token=refresh_token_str,
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
    return generate_and_store_tokens(authorization=authorization, user_account=user_account, client_id=client_id, scopes=authorization.consented_scopes)

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
    invalid_hash: str = hash_string("INVALIDATED") # Required for bcrypt comparison
    authorization.hashed_refresh_token = invalid_hash
    response: int = db_manager.authorization_interface.update_authorization(authorization)
    return True if response == 0 else False

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
    if not verify_token_hash(token=decoded_token, token_type=TokenType.REFRESH): 
        invalidate_refresh_token(username=decoded_token.sub)
        return None
    user_account: Account = db_manager.accounts_interface.get_account(username=decoded_token.sub)
    if not user_account: return None
    authorization: Authorization = db_manager.authorization_interface.get_authorization(username=decoded_token.sub)
    return generate_and_store_tokens(authorization=authorization, user_account=user_account, 
                                     client_id=decoded_token.aud, scopes=authorization.consented_scopes)

def generate_and_store_auth_code(state: str, username: str, code_challenge: str, consented_scopes: str) -> AuthorizeResponse:
    """
    Generate an authorization code and store it in the database with the provided state, username, code challenge and scopes.

    Args:
        state (str): The CSRF state.
        username (str): The username of the user.
        code_challenge (str): The code challenge for the authorization code provided by the client.
        consented_scopes (str): The scopes the user has consented to.

    Returns:
        AuthorizeResponse: The response containing the authorization code and CSRF state.
    """
    encrypted_auth_code, authorization_code = generate_authorization_code(username=username)
    csrf_state: str = state
    user_authorization: Authorization = Authorization(
        username=username,
        auth_code=authorization_code,
        code_challenge=code_challenge,
        hashed_refresh_token=None,
        consented_scopes=consented_scopes
    )
    response: int = db_manager.authorization_interface.update_authorization(authorization=user_authorization)
    if response == -1: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Authorization failed.")
    return AuthorizeResponse(authorization_code=encrypted_auth_code, state=csrf_state)
    
def get_client_scopes_from_profile_scopes(profile_scopes: list[ProfileScope]) -> list[ClientScope]:
    """
    Converts a list of profile scopes to a list of client scopes.

    Args:
        profile_scopes (list[ProfileScope]): The list of profile scopes to be converted.

    Returns:
        list[ClientScope]: The list of client scopes. None if the profile scopes are invalid.
    """
    if len(profile_scopes) == 0: return []
    client_scope_list: list[ClientScope] = []
    client_to_scope: dict[str, list[ProfileScope]] = {scope.client_id: [] for scope in profile_scopes}
    for scope in profile_scopes:
        client_to_scope[scope.client_id].append(scope)
    for client_id, scope_list in client_to_scope.items():
        client: Client = db_manager.clients_interface.get_client(client_id=client_id)
        if not client: return None
        for c_scope in client.scopes:
            if c_scope.name in [scope.scope for scope in scope_list]:
                client_scope_list.append(c_scope)
    if len(client_scope_list) != len(profile_scopes): return None
    return client_scope_list

def get_mapped_client_scopes_from_profile_scopes(profile_scopes: list[ProfileScope]) -> dict[str, list[ClientScope]]:
    """
    Convert a list of profile scopes to a dictionary of client_ids mapped to a list of client scopes.

    Args:
        profile_scopes (list[ProfileScope]): The list of profile scopes to be converted.

    Returns:
        dict[str, list[ClientScope]]: The dictionary of client ids mapped to a list of client scopes. None if the profile scopes are invalid.
    """
    if len(profile_scopes) == 0: return []
    client_to_profile_scope: dict[str, list[ProfileScope]] = {scope.client_id: [] for scope in profile_scopes}
    for scope in profile_scopes:
        client_to_profile_scope[scope.client_id].append(scope)
    client_id_to_client_scopes: dict[str, list[ClientScope]] = {}
    for client_id, p_scopes in client_to_profile_scope.items():
        client_scopes: list[ClientScope] = get_client_scopes_from_profile_scopes(profile_scopes=p_scopes)
        if not client_scopes: return None
        client_id_to_client_scopes[client_id] = client_scopes
    return client_id_to_client_scopes
    
    
def get_consent_details(client_id: str, requested_scopes: list[ProfileScope], 
                        username: str) -> ConsentDetails:
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
    requested_scopes_as_client_scopes: list[ClientScope] = get_client_scopes_from_profile_scopes(
        profile_scopes=requested_scopes
    )
    client_non_personal_scopes: list[ClientScope] = [scope for scope in client.scopes if not scope.is_personal_scope]
    comma_seperated_public_metadata_attributes: dict[str, str] = {key: ", ".join([v.value for v in value]) for key, value in map_attributes_to_access_types(scopes=client_non_personal_scopes, metadata_attributes=True).items()}
    comma_seperated_public_account_attributes: dict[str, str] = {key: ", ".join([v.value for v in value]) for key, value in map_attributes_to_access_types(scopes=client_non_personal_scopes, metadata_attributes=False).items()}
    consent_details: ConsentDetails = ConsentDetails(name=client.name, 
                                                     description=client.description, 
                                                     requested_scopes=requested_scopes_as_client_scopes,
                                                     account_connected=check_profile_exists(username=username,
                                                                                            client_id=client_id),
                                                     client_redirect_uri=client.redirect_uri,
                                                     client_metadata_attributes=client.profile_metadata_attributes,
                                                     client_public_metadata_attributes=comma_seperated_public_metadata_attributes,
                                                     client_shared_account_attributes=comma_seperated_public_account_attributes,
                                                     )
    return consent_details
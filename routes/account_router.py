from secrets import token_urlsafe
from fastapi import Depends, APIRouter, status, HTTPException, Request, Response
import httpx
from starlette.templating import _TemplateResponse
from common import AUTH_CLIENT_ID, AUTH_CLIENT_SECRET, RECAPTCHA_SITE_KEY, templates, bearer_token_auth
from models.account_models import Account, Profile
from models.form_models import UserRegistrationForm
from models.request_models import AuthorizationRequest, GrantType, TokenRequest
from models.scope_models import ScopeAccessType, ScopeAttribute
from models.util_models import AuthenticatedAccount
from services.account_services import get_attributes_from_scopes, register_account_in_db_collections
from utils.account_utils import get_profile_from_account
from utils.auth_utils import generate_code_challenge_and_verifier
from utils.password_manager import PasswordManager
from utils.web_utils import configure_redirect_uri
from validators.account_validators import check_user_exists

router = APIRouter(
    prefix="/account",
    tags=["Accounts"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_account(form_data: UserRegistrationForm = Depends()):
    """
    Register a new account.

    Args:
        form_data (UserRegistrationForm): The form data for the new account.
    """
    hashed_password: str = PasswordManager.get_password_hash(form_data.password)
    new_account: Account = Account(
        username=form_data.username,
        display_name=form_data.display_name,
        email=form_data.email,
        hashed_password=hashed_password,
        hashed_totp_pin=None,
        profiles=[]
    )
    if check_user_exists(username=new_account.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="User already exists.")
    response: int = register_account_in_db_collections(new_account=new_account)
    if response == 0:
        return "Account registered successfully."
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        detail="Account registration failed.")
    
@router.get("/login", status_code=status.HTTP_200_OK)
async def login_account(request: Request, response: Response):
    code_challenge, code_verifier = generate_code_challenge_and_verifier()
    state: str = token_urlsafe(256)
    login_auth_request: AuthorizationRequest = AuthorizationRequest(
        client_id=AUTH_CLIENT_ID,
        client_secret=AUTH_CLIENT_SECRET,
        response_type="code",
        state=state,
        code_challenge=code_challenge,
        scope=""
    )
    configured_response: _TemplateResponse = templates.TemplateResponse("login.html", {"recaptcha_site_key": RECAPTCHA_SITE_KEY,
                                                     "request": request,
                                                     "request_data": login_auth_request.model_dump()})
    configured_response.set_cookie(key="code_verifier", value=code_verifier, httponly=True, secure=False)
    configured_response.set_cookie(key="state", value=state, httponly=True, secure=False)
    return configured_response
    
@router.get("/login/callback", status_code=status.HTTP_200_OK)
async def login_account_callback(request: Request, response: Response, code: str, state: str):
    if not code or not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid callback parameters.")
    code_verifier_cookie: str = request.cookies.get("code_verifier")
    state_cookie_cookie: str = request.cookies.get("state")
    if not code_verifier_cookie or not state_cookie_cookie:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Missing code verifier and CSRF cookies.")
    if state != state_cookie_cookie:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="CSRF state mismatch.")
    token_request: TokenRequest = TokenRequest(grant_type=GrantType.AUTHORIZATION_CODE,
                                               client_id=AUTH_CLIENT_ID,
                                               client_secret=AUTH_CLIENT_SECRET,
                                               code=code,
                                               code_verifier=code_verifier_cookie,
                                               refresh_token=None,)
    configured_token_url: str = configure_redirect_uri(base_uri=f"{request.base_url}authentication/token", 
                                                          query_parameters=token_request.model_dump()) 
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(configured_token_url)
            token_response.raise_for_status()
            token_data = token_response.json()
            return token_data
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get token.")
    
@router.get("/{username}", status_code=status.HTTP_200_OK)
async def get_account_information(username: str, account: AuthenticatedAccount = Depends(bearer_token_auth)):
    """
    Returns all account information for the specified account that the requesting account has access to (based on the bearer token scopes).
    
    TODO: Currently only allows the account to get its own information.

    Args:
        username (str): The username of the account to get.
        account (AuthenticatedAccount): The account making the request. Depends on the bearer token.
        
    Response:
        dict: The attributes of the account mapped to the values retrieved.
        
        Example:
        ```json
        {
            "username": "test",
            "display_name": "Test User",
            "attributes": {
                "<client_id>.example_attribute": "Example Value",
            }
        }
        ```
    """
    if account.username != username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Account does not have access to this information.")
    attributes: dict[str, list[ScopeAttribute]] = get_attributes_from_scopes(scopes=account.request_scopes)
    if not attributes:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Failed to get account information.")
    account_info: dict[str, any] = {
        "username": account.username,
        "display_name": account.display_name,
        "attributes": {}
    }
    for client_id, scope_attribute in attributes.items():
        client_profile: Profile = get_profile_from_account(account=account, client_id=client_id)
        if client_profile:
            for attribute in scope_attribute:
                if attribute.access_type == ScopeAccessType.READ:
                    metadata_attribute: any = client_profile.metadata.get(attribute.attribute_name)
                    if metadata_attribute:
                        account_info["attributes"][f"{client_id}.{attribute.attribute_name}"] = metadata_attribute
    return account_info
from secrets import token_urlsafe
from fastapi import Depends, APIRouter, status, HTTPException, Request, Response
import httpx
from starlette.templating import _TemplateResponse
from common import AUTH_CLIENT_ID, AUTH_CLIENT_SECRET, RECAPTCHA_SITE_KEY, templates, bearer_token_auth
from models.account_models import Account
from models.form_models import UserRegistrationForm
from models.request_models import AuthorizationRequest, GrantType, TokenRequest
from models.scope_models import AccountAttribute, ProfileScope, ScopeAccessType
from models.util_models import AuthenticatedAccount
from services.account_services import get_account_attributes, get_scoped_account_attributes, register_account_in_db_collections
from services.client_services import get_shared_read_attributes
from utils.auth_utils import generate_code_challenge_and_verifier
from utils.password_manager import PasswordManager
from utils.scope_utils import str_to_list_of_profile_scopes
from utils.web_utils import configure_redirect_uri
from validators.account_validators import check_profile_exists, check_user_exists

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
        scope=f"{AUTH_CLIENT_ID}.read:sauce"
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
async def get_account(username: str, account: AuthenticatedAccount = Depends(bearer_token_auth)):
    """
    Get the requested user's account information as a dictionary of values.
    
    The dictionary will only contain the information about the user authorized by the request scopes.

    Args:
        username (str): The username of the account to get.
        account (AuthenticatedAccount): The account making the request based on the access token.
    """
    if not check_user_exists(username=username):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User does not exist.")
    if not check_profile_exists(username=username, client_id=account.access_token.aud):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="User account is not linked to the client.")
    if account.access_token.scope == "": return {}
    read_only_attributes: list[AccountAttribute] = get_shared_read_attributes(client_id=account.access_token.aud)
    if not read_only_attributes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Some clients in the access token audience do not exist.")
    requested_scopes: list[ProfileScope] = str_to_list_of_profile_scopes(scopes_str_list=account.access_token.scope)
    if not requested_scopes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid scopes in access token.")
    scoped_account_information: dict[str, any] = get_scoped_account_attributes(username=username, scopes=requested_scopes,
                                                                               allowed_access_types=[ScopeAccessType.READ])
    if not scoped_account_information: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="User account does not have the required information to fulfill the request.")
    retreived_account_attributes: dict[str, any] = get_account_attributes(username=username, attributes=read_only_attributes)
    if not retreived_account_attributes:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Issue fetching account information.")
    scoped_account_information.update(retreived_account_attributes)
    return scoped_account_information
from secrets import token_urlsafe
from fastapi import Depends, APIRouter, status, HTTPException, Request, Response
from fastapi.datastructures import FormData
from fastapi.responses import HTMLResponse
import httpx
from starlette.templating import _TemplateResponse
from validators.web_validators import verify_captcha_completed
from common import templates, bearer_token_auth, config
from models.account_models import Account
from models.form_models import UserRegistrationForm
from models.request_models import AuthorizationRequest, GrantType, TokenRequest, UpdateAccountRequest
from models.scope_models import ProfileScope, ScopeAccessType
from models.util_models import AuthenticatedAccount
from services.account_services import get_scoped_account_attributes, register_account_in_db_collections, update_existing_attributes
from utils.auth_utils import generate_code_challenge_and_verifier
from utils.password_manager import PasswordManager
from utils.scope_utils import str_to_list_of_profile_scopes
from utils.web_utils import configure_redirect_uri, form_to_object
from validators.account_validators import check_profile_exists, check_user_exists

router = APIRouter(
    prefix="/account",
    tags=["Accounts"]
)

@router.get("/register", response_class=HTMLResponse)
async def register_account_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request,
                                                     "recaptcha_site_key": config.google_recaptcha_config.site_key})
    
@router.post("/register", status_code=status.HTTP_200_OK)
async def register_account_submit(request: Request):
    """
    Register the account based on the form data and return a redirect response to the login page.
    """
    fetched_form_data: FormData = await request.form()
    form_data: UserRegistrationForm = form_to_object(form_data=fetched_form_data, object_class=UserRegistrationForm)
    hashed_password: str = PasswordManager.get_password_hash(form_data.password)
    if not verify_captcha_completed(captcha_response=form_data.g_recaptcha_response):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Captcha verification failed.")
    if check_user_exists(username=form_data.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="User already exists.")
    new_account: Account = Account(
        username=form_data.username,
        display_name=form_data.display_name,
        email=form_data.email,
        hashed_password=hashed_password,
        profiles=[]
    )
    response: int = register_account_in_db_collections(new_account=new_account)
    if response != 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Account registration failed.")
    return "Account registered successfully."
    
@router.get("/login", status_code=status.HTTP_200_OK)
async def login_account(request: Request, response: Response):
    code_challenge, code_verifier = generate_code_challenge_and_verifier()
    state: str = token_urlsafe(256)
    login_auth_request: AuthorizationRequest = AuthorizationRequest(
        client_id=config.default_client_config.client_id,
        client_secret=config.default_client_config.client_secret,
        response_type="code",
        state=state,
        code_challenge=code_challenge,
        scope=""
    )
    configured_response: _TemplateResponse = templates.TemplateResponse("login.html", {"recaptcha_site_key": config.google_recaptcha_config.site_key,
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
                                               client_id=config.default_client_config.client_id,
                                               client_secret=config.default_client_config.client_secret,
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
    if username == "me": username = account.username
    if not check_user_exists(username=username):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User does not exist.")
    if not check_profile_exists(username=username, client_id=account.access_token.aud):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="User account is not linked to the client.")
    requested_scopes: list[ProfileScope] = str_to_list_of_profile_scopes(scopes_str_list=account.access_token.scope)
    if requested_scopes == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Invalid scopes in access token.")
    scoped_account_information: dict[str, any] = get_scoped_account_attributes(username=username, scopes=requested_scopes,
                                                                               allowed_access_types=[ScopeAccessType.READ],
                                                                               is_personal=username==account.username)
    if scoped_account_information == None: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="User account does not have the required information to fulfill the request.")
    scoped_account_information["username"] = username
    return scoped_account_information

@router.patch("/{username}", status_code=status.HTTP_200_OK)
async def update_account(username: str, update_account_request: UpdateAccountRequest, account: AuthenticatedAccount = Depends(bearer_token_auth)):
    """
    Update the account information for the given username based on the request scopes.
    
    NOTE: 
    - If an attribute in the attribute_updates dictionary does not exist for the user, an error will be raised.
    - If the scopes don't allow the update of an attribute, an error will be raised.

    Args:
        username (str): The username of the account to update.
        update_account_request (UpdateAccountRequest): The request to update the account information.
        account (AuthenticatedAccount): The account making the request based on the access token.
    """
    if update_account_request.attribute_updates == {}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No attributes to update.")
    if not check_user_exists(username=username):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User does not exist.")
    if not check_profile_exists(username=username, client_id=account.access_token.aud):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="User account is not linked to the client.")
    if account.access_token.scope == "": return None
    requested_scopes: list[ProfileScope] = str_to_list_of_profile_scopes(scopes_str_list=account.access_token.scope)
    if requested_scopes == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Invalid scopes in access token.")
    all_allowed_write_attributes: dict[str, any] = get_scoped_account_attributes(username=username, 
                                                                                 scopes=requested_scopes, 
                                                                                 allowed_access_types=[ScopeAccessType.WRITE],
                                                                                 is_personal=username==account.username)
    if all_allowed_write_attributes == None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Issue handling scopes.")
    for attribute, _ in update_account_request.attribute_updates.items():
        if attribute not in all_allowed_write_attributes:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Scope does not allow for updating the attribute.")
    response: int = update_existing_attributes(username=username, attribute_updates=update_account_request.attribute_updates)
    if response == -1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Issue updating account information.")
    return "Account information updated successfully."
    
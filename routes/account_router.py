from fastapi import Depends, APIRouter, status, HTTPException, Request, Response
from routes.account.models import UserRegistrationForm
from database.models import Account
from routes.account.account_utils import *
from routes.authentication.password_manager import PasswordManager
from fastapi.templating import Jinja2Templates
from routes.authentication.models import AuthorizationRequest, TokenRequest, GrantType
from routes.authentication.authentication_utils import configure_redirect_uri
import httpx
from starlette.templating import _TemplateResponse
import os

router = APIRouter(
    prefix="/account",
    tags=["Accounts"]
)
templates = Jinja2Templates(directory="templates")

AUTH_CLIENT_ID: str = os.getenv('AUTH_CLIENT_ID')
AUTH_CLIENT_SECRET: str = os.getenv('AUTH_CLIENT_SECRET')
RECAPTCHA_SITE_KEY: str = os.getenv('RECAPTCHA_SITE_KEY')

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
        scope="read:profile write:profile",
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
            print(f"DEBUG: {token_response.json()}")
            token_response.raise_for_status()  # Raise an exception for non-2xx status codes
            token_data = token_response.json()
            return token_data
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get token.")
    
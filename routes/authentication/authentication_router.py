from fastapi import APIRouter, status, Depends, HTTPException, Query
from routes.authentication.authentication_utils import *
from routes.authentication.models import AuthorizationRequest, AuthorizeResponse, TokenForm, GrantType, TokenResponse, LoginForm, ConcentForm
from database.models import Authorization
from starlette.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/authentication",
    tags=["Authentication"]
)
templates = Jinja2Templates(directory="templates")

@router.get("/authorize", status_code=status.HTTP_200_OK)
async def authorize_endpoint(request: Request, request_data: AuthorizationRequest = Depends()):
    """
    Validate client credentials and requested scopes.
    Redirects to login page if the client is valid.
    Conforms to OAuth2.0 Authorization Code Flow with Proof Key for Code Exchange (PKCE).
    """
    if not valid_client_credentials(client_id=request_data.client_id, 
                                    client_secret=request_data.client_secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid client credentials.")
    if not valid_client_scopes(client_id=request_data.client_id, 
                                   scopes=request_data.scope):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Invalid client scopes.")
    configured_redirect_url: str = configure_redirect_uri(base_uri=None, 
                                                          query_parameters=request_data.model_dump()) 
    return RedirectResponse(url=configured_redirect_url)

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, request_data: AuthorizationRequest = Depends()): 
    """
    Display the login form to the user, passing the request and request_data to the template.
    """
    return templates.TemplateResponse("login.html", {"request": request, 
                                                     "request_data": request_data})

@router.post("/login", response_class=HTMLResponse)
async def login_submit(form_data: LoginForm = Depends()): 
    """
    Validate the user credentials and redirect to the consent page if the user is valid.
    """
    if validate_user_credentials(username=form_data.username, 
                                 password=form_data.password) == -1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials.")
    configured_redirect_url: str = configure_redirect_uri(base_uri=None, 
                                                          query_parameters=form_data.model_dump())
    return RedirectResponse(url=configured_redirect_url)

@router.post("/token", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def get_access_token(form_data: TokenForm = Depends()):
    """
    Get access token using the provided grant type.
    Complies with OAuth2.0 Authorization Code Flow with Proof Key for Code Exchange (PKCE).

    Args:
        form_data (TokenForm): TokenForm object containing the OAuth2.0 /token request parameters.
    """
    token_response: TokenResponse = None
    match form_data.grant_type:
        case GrantType.AUTHORIZATION_CODE:
            token_response = get_tokens_with_authorization_code(
                auth_code=form_data.code,
                code_verifier=form_data.code_verifier,
                client_id=form_data.client_id,
                client_secret=form_data.client_secret
            )
            if not token_response: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid authorization code.")
        case GrantType.REFRESH_TOKEN:
            if form_data.refresh_token is None: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Refresh token is required for this grant type.")
            token_response = get_tokens_with_refresh_token(
                refresh_token=form_data.refresh_token)
            if not token_response: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid refresh token.")
    if not token_response: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Token generation failed.")
    return token_response.model_dump()
            
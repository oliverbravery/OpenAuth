from fastapi import APIRouter, status, Depends, HTTPException
from routes.authentication.authentication_utils import *
from routes.authentication.models import AuthorizationRequest, AuthorizeResponse, TokenForm, GrantType, TokenResponse, LoginForm, ConcentForm, Endpoints
from starlette.responses import RedirectResponse
from starlette.formparsers import FormData
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/authentication",
    tags=["Authentication"]
)

templates = Jinja2Templates(directory="templates")

recaptcha_site_key: str = os.getenv('RECAPTCHA_SITE_KEY')

@router.get("/authorize", status_code=status.HTTP_200_OK)
async def authorize_endpoint(request_data: AuthorizationRequest = Depends()):
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
                                   scopes=request_data.get_scopes_as_list()):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Invalid client scopes.")
    configured_redirect_url: str = configure_redirect_uri(base_uri=Endpoints.LOGIN.value, 
                                                          query_parameters=request_data.model_dump()) 
    return RedirectResponse(url=configured_redirect_url)

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, request_data: AuthorizationRequest = Depends()): 
    """
    Display the login form to the user, passing the request and request_data to the template.
    """
    return templates.TemplateResponse("login.html", {"request": request,
                                                     "request_data": request_data,
                                                     "recaptcha_site_key": recaptcha_site_key})

@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request): 
    """
    Validate the user credentials and redirect to the consent page if the user is valid.
    """
    fetched_form_data: FormData = await request.form()
    form_data: LoginForm = form_to_object(form_data=fetched_form_data, object_class=LoginForm)
    if not verify_captcha_completed(captcha_response=form_data.g_recaptcha_response):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Captcha verification failed.")
    if validate_user_credentials(username=form_data.username, 
                                 password=form_data.password) == -1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials.")
    concent_details: ConcentDetails = get_client_concent_details(client_id=form_data.client_id, 
                                                                 scopes=form_data.scope)
    return templates.TemplateResponse("consent.html", {"request": request,
                                                       "request_data": form_data, 
                                                       "concent_details": concent_details})

@router.post("/consent", response_class=HTMLResponse)
async def consent_submit(request: Request):
    """
    Generate and store an authorization code, redirecting to redirect_uri with code and CSRF state.
    """
    fetched_form_data: FormData = await request.form()
    form_data: ConcentForm = form_to_object(form_data=fetched_form_data, object_class=ConcentForm)
    if form_data.consented != 'true':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User did not consent to the scopes requested.")
    authorize_response: AuthorizeResponse = generate_and_store_auth_code(username=form_data.username,
                                                                        state=form_data.state,
                                                                        code_challenge=form_data.code_challenge)
    if authorize_response is None: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Authorization code generation failed.")
    configured_redirect_url: str = configure_redirect_uri(base_uri=form_data.client_redirect_uri, 
                                                        query_parameters={
                                                            "code": authorize_response.authorization_code,
                                                            "state": authorize_response.state
                                                        })
    return RedirectResponse(url=configured_redirect_url)

@router.post("/token", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def get_access_token(form_data: TokenForm = Depends()):
    """
    Get access token using the provided grant type.
    Complies with OAuth2.0 Authorization Code Flow with Proof Key for Code Exchange (PKCE).

    Args:
        form_data (TokenForm): TokenForm object containing the OAuth2.0 /token request parameters.
    """
    # TODO: Check that the parameters should be passed in the query or in the query
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
            
from fastapi import APIRouter, status, Depends, HTTPException
from routes.authentication.authentication_utils import *
from routes.authentication.models import AuthorizationForm, AuthorizeResponse, TokenForm, GrantType, TokenResponse
from database.models import Authorization

router = APIRouter(
    prefix="/authentication",
    tags=["Authentication"]
)

@router.get("/authorize", status_code=status.HTTP_200_OK, response_model=AuthorizeResponse)
async def register_account(form_data: AuthorizationForm = Depends()):
    if validate_user_credentials(username=form_data.username, password=form_data.password) == -1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials.")
    authorization_code: str = generate_authorization_code(username=form_data.username)
    csrf_state: str = form_data.state
    code_challenge: str = form_data.code_challenge
    user_authorization: Authorization = Authorization(
        username=form_data.username,
        authorization_code=authorization_code,
        code_challenge=code_challenge,
        hashed_refresh_token=None
    )
    response: int = db_manager.authorization_interface.update_authorization(authorization=user_authorization)
    if response == -1: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Authorization failed.")
    return AuthorizeResponse(authorization_code=authorization_code, csrf_state=csrf_state).model_dump()

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
            
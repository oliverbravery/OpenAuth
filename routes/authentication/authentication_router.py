from fastapi import APIRouter, status, Depends, HTTPException
from routes.authentication.authentication_utils import *
from routes.authentication.models import AuthorizationForm, AuthorizeResponse
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
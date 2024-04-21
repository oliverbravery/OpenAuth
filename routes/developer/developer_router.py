from fastapi import APIRouter, status, Depends, HTTPException
from routes.authentication.authentication_utils import BearerTokenAuth
from database.models import Account, AccountRole
from routes.developer.developer_utils import *

router = APIRouter(
    prefix="/developer",
    tags=["Developer"]
)

bearer_token_auth: BearerTokenAuth = BearerTokenAuth()

@router.get("/enroll", status_code=status.HTTP_200_OK)
async def enroll_developer(account: Account = Depends(bearer_token_auth)):
    """
    Enroll the current account as a developer.
    """
    if account.account_role == AccountRole.DEVELOPER:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Account is already enrolled as a developer.")
    if enroll_user_as_developer(account) == -1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Failed to enroll account as a developer.")
    return "Account successfully enrolled as a developer."
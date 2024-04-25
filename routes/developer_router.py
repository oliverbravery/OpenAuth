from fastapi import APIRouter, status, Depends, HTTPException

from models.account_models import Account, AccountRole
from services.auth_services import BearerTokenAuth
from services.account_services import enroll_account_as_developer

router = APIRouter(
    prefix="/developer",
    tags=["Developer"]
)

bearer_token_auth: BearerTokenAuth = BearerTokenAuth()

@router.post("/enroll", status_code=status.HTTP_200_OK)
async def enroll_developer(account: Account = Depends(bearer_token_auth)):
    """
    Enroll the current account as a developer.
    """
    if account.account_role == AccountRole.DEVELOPER:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Account is already enrolled as a developer.")
    if enroll_account_as_developer(account) == -1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Failed to enroll account as a developer.")
    return "Account successfully enrolled as a developer."
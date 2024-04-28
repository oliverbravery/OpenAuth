from fastapi import APIRouter, status, Depends, HTTPException

from models.account_models import Account, AccountRole
from services.auth_services import BearerTokenAuth
from services.account_services import enroll_account_as_developer
from validators.account_validators import verify_account_is_developer

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
    verify_account_is_developer(account=account)
    if enroll_account_as_developer(account) == -1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Failed to enroll account as a developer.")
    return "Account successfully enrolled as a developer."
from fastapi import APIRouter, status, Depends, HTTPException

from models.account_models import Account, AccountRole
from models.form_models import ClientRegistrationForm
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

@router.post("/add-client", status_code=status.HTTP_200_OK)
async def add_client(client_registration_form: ClientRegistrationForm, account: Account = Depends(bearer_token_auth)):
    """
    Add a new client to the database.
    """
    verify_account_is_developer(account=account)
    # TODO: Validate the client and it's scopes
    # TODO: Generate a client_id and client_secret
    # TODO: Add the client to the database
    # TODO: Return the client_id and client_secret
    
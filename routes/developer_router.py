from fastapi import APIRouter, status, Depends, HTTPException

from models.account_models import AccountRole
from models.client_models import Client
from models.form_models import ClientRegistrationForm
from models.util_models import AuthenticatedAccount, ClientCredentialType
from services.account_services import enroll_account_as_developer
from services.client_services import generate_unique_client_id
from utils.client_utils import generate_client_credential
from utils.hash_utils import hash_string
from validators.account_validators import verify_account_is_developer
from validators.client_validators import validate_client_developers, validate_metadata_attributes, validate_profile_defaults
from validators.scope_validators import validate_client_scopes
from common import db_manager, bearer_token_auth

router = APIRouter(
    prefix="/developer",
    tags=["Developer"]
)

@router.post("/enroll", status_code=status.HTTP_200_OK)
async def enroll_developer(account: AuthenticatedAccount = Depends(bearer_token_auth)):
    """
    Enroll the current account as a developer.
    """
    if account.account_role != AccountRole.DEVELOPER:
        if enroll_account_as_developer(account) == -1:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="Failed to enroll account as a developer.")
    return "Account is enrolled as a developer."

@router.post("/add-client", status_code=status.HTTP_200_OK)
async def add_client(client_registration_form: ClientRegistrationForm, account: AuthenticatedAccount = Depends(bearer_token_auth)):
    """
    Add a new client to the database.
    """
    verify_account_is_developer(account=account)
    new_client: Client = Client(
        client_id="EXAMPLE",
        client_secret_hash="EXAMPLE",
        name=client_registration_form.client_name,
        description=client_registration_form.client_description,
        redirect_uri=client_registration_form.client_redirect_uri,
        developers=client_registration_form.client_developers,
        scopes=client_registration_form.client_scopes,
        profile_metadata_attributes=client_registration_form.client_profile_metadata_attributes,
        profile_defaults=client_registration_form.client_profile_defaults
    )
    if not validate_client_developers(client=new_client):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Client developers must be valid developer accounts with developer only scopes.")
    if not validate_metadata_attributes(client=new_client):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Metadata attributes must have unique names.")
    if not validate_profile_defaults(client=new_client):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Profile defaults must exist in profile metadata attributes and be of the correct type.")
    if not validate_client_scopes(client=new_client):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Client scopes must have unique names and their associated attributes must exist in the profile metadata attributes.")
    new_client.client_id = generate_unique_client_id()
    plaintext_client_secret: str = generate_client_credential(credential_type=ClientCredentialType.SECRET)
    new_client.client_secret_hash = hash_string(plaintext=plaintext_client_secret)
    response: int = db_manager.clients_interface.add_client(client=new_client)
    if response == -1:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Failed to add client to the database.")
    return {"client_id": new_client.client_id, "client_secret": plaintext_client_secret}
    
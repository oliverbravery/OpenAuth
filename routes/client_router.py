from fastapi import APIRouter, HTTPException, status, Depends
from models.request_models import ValidateTokenRequest
from common import bearer_token_auth
from models.util_models import AuthenticatedAccount


router = APIRouter(
    prefix="/client",
    tags=["Client"]
)

@router.get("/validate-token/{client_id}", status_code=status.HTTP_200_OK)
def validate_token(client_id: str, validating_properties: ValidateTokenRequest, authenticated_account: AuthenticatedAccount = Depends(bearer_token_auth)):
    """
    Validate the token for the client. Checks if the client_id is in the audience of the access token and the token is valid.
    
    Args:
        client_id (str): Client id to validate the token for.
        validating_properties (dict[StandardAccountAttributes,any]): Properties to validate the token account against.
    """
    if authenticated_account.access_token.aud != client_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Client id does not match token audience.")
    for key, value in validating_properties.validating_properties.items():
        if not hasattr(authenticated_account, key.value):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Account does not have property {key.value}.")
        if getattr(authenticated_account, key.value) != value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Account property {key.value} does not match.")
    return {"message": "Token is valid."}
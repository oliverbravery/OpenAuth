from fastapi import APIRouter, HTTPException, status, Depends
from common import bearer_token_auth
from models.util_models import AuthenticatedAccount


router = APIRouter(
    prefix="/client",
    tags=["Client"]
)

@router.get("/validate-token/{client_id}", status_code=status.HTTP_200_OK)
def validate_token(client_id: str, authenticated_account: AuthenticatedAccount = Depends(bearer_token_auth)):
    """
    Validate the token for the client. Checks if the client_id is in the audience of the access token and the token is valid.
    
    Args:
        client_id (str): Client id to validate the token for.
    """
    if authenticated_account.access_token.aud != client_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Client id does not match token audience.")
    return {"message": "Token is valid."}
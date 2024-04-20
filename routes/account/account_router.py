from fastapi import Depends, APIRouter, status, HTTPException
from routes.account.models import UserRegistrationForm
from database.models import Account
from routes.account.account_utils import *

router = APIRouter(
    prefix="/account",
    tags=["Accounts"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_account(form_data: UserRegistrationForm = Depends()):
    """
    Register a new account.

    Args:
        form_data (UserRegistrationForm): The form data for the new account.
    """
    new_account: Account = Account(
        username=form_data.username,
        display_name=form_data.display_name,
        email=form_data.email,
        hashed_password=form_data.password,
        hashed_totp_pin=None,
        profiles=[]
    )
    if check_user_exists(username=new_account.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="User already exists.")
    response: int = register_account_in_db_collections(new_account=new_account)
    if response == 0:
        return "Account registered successfully."
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        detail="Account registration failed.")
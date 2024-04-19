from fastapi import APIRouter
from fastapi import Depends
from routes.account.models import NewAccountForm
from models import Account
from main import db_manager
from routes.account.account_utils import *

router = APIRouter(
    prefix="/account",
    tags=["Accounts"]
)

@router.post("/register")
async def register_account(form_data: NewAccountForm = Depends()):
    """
    Register a new account.

    Args:
        form_data (NewAccountForm): The form data for the new account.
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
        return {"status": "Error", "message": "User already exists."}
    response: int = db_manager.accounts_interface.add_account(account=new_account)
    if response == 1:
        return {"status": "Success", "message": "Account registered successfully."}
    return {"status": "Error", "message": "Account registration failed."}
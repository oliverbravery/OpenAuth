from fastapi import APIRouter
from main import db_manager
from fastapi import Depends
from routes.account.models import NewAccountForm

router = APIRouter(
    prefix="/account",
    tags=["Accounts"]
)

@router.post("/register")
async def register_account(form_data: NewAccountForm = Depends()):
    return {"status": "Success", "message": "Account registered successfully."}
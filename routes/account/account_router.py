from fastapi import APIRouter
from main import db_manager

router = APIRouter(
    prefix="/account",
    tags=["Accounts"]
)

@router.post("/register")
async def register_account():
    return {"status": "Success", "message": "Account registered successfully."}
from fastapi import APIRouter

router = APIRouter(
    prefix="/account",
    tags=["Accounts"]
)

@router.post("/register")
async def register_account():
    return {"status": "Success", "message": "Account registered successfully."}
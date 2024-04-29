from fastapi import APIRouter
from common import token_manager


router = APIRouter(
    prefix="/.well-known",
    tags=["Well Known"]
)

@router.get("/jwks.json")
def get_jwks():
    """
    Get the JWKS for the API.
    """
    return token_manager.generate_jwks_dict()
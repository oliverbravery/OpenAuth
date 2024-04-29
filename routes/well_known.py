from fastapi import APIRouter


router = APIRouter(
    prefix="/.well-known",
    tags=["Well Known"]
)
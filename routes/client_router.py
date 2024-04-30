from fastapi import APIRouter


router = APIRouter(
    prefix="/client",
    tags=["Client"]
)
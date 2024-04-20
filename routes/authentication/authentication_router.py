from fastapi import APIRouter
from routes.authentication.authentication_utils import *

router = APIRouter(
    prefix="/authentication",
    tags=["Authentication"]
)
from main import db_manager
from database.models import Account, Authorization, Client, Profile
from routes.authentication.password_manager import PasswordManager
from routes.authentication.token_manager import TokenManager
from routes.authentication.models import TokenType, TokenResponse, RefreshToken, AccessToken, AuthorizeResponse, ConcentDetails
from secrets import token_urlsafe
import os
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode, urlsafe_b64decode
import hashlib
import bcrypt
from fastapi import HTTPException, status
from starlette.requests import Request
import httpx
from httpx import Response
from starlette.formparsers import FormData
from pydantic import BaseModel

fernet: Fernet = Fernet(os.getenv("AUTH_CODE_SECRET"))

recaptcha_secret_key: str = os.getenv("RECAPTCHA_SECRET_KEY")
if not recaptcha_secret_key: raise ValueError("RECAPTCHA_SECRET_KEY not set in environment variables.")
google_verify_url: str = f"https://www.google.com/recaptcha/api/siteverify?secret={recaptcha_secret_key}&response="

token_manager: TokenManager = TokenManager(
    access_token_expire_time=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")),
    refresh_token_expire_time=int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")),
    private_key_path=str(os.getenv("JWT_PRIVATE_PEM_PATH")),
    public_key_path=str(os.getenv("JWT_PUBLIC_PEM_PATH")),
    token_algorithm=str(os.getenv("TOKEN_ALGORITHM"))
)
        
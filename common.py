from fastapi.templating import Jinja2Templates
from database.db_manager import DBManager
from cryptography.fernet import Fernet
from services.auth_services import BearerTokenAuth
from utils.token_manager import TokenManager
from utils.database_utils import get_connection_string
from dotenv import load_dotenv
import os

load_dotenv(override=True)

MONGO_PORT: int = os.getenv("MONGO_PORT")
MONGO_HOST: str = os.getenv("MONGO_HOST")
MONGO_ROOT_USERNAME: str = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_ROOT_PASSWORD: str = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_DATABASE_NAME: str = os.getenv("DMONGO_DATABASE_NAME")
RECAPTCHA_SECRET_KEY: str = os.getenv("RECAPTCHA_SECRET_KEY")
AUTH_CODE_SECRET: str = os.getenv("AUTH_CODE_SECRET")
ACCESS_TOKEN_EXPIRE_MINUTES: str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_MINUTES: str = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")
JWT_PRIVATE_PEM_PATH: str = os.getenv("JWT_PRIVATE_PEM_PATH")
JWT_PUBLIC_PEM_PATH: str = os.getenv("JWT_PUBLIC_PEM_PATH")
TOKEN_ALGORITHM: str = os.getenv("TOKEN_ALGORITHM")
AUTH_CLIENT_ID: str = os.getenv("AUTH_CLIENT_ID")
AUTH_CLIENT_SECRET: str = os.getenv("AUTH_CLIENT_SECRET")
AUTH_SERVICE_HOST: str = os.getenv("AUTH_SERVICE_HOST")
AUTH_SERVICE_PORT: str = os.getenv("AUTH_SERVICE_PORT")
RECAPTCHA_SITE_KEY: str = os.getenv("RECAPTCHA_SITE_KEY")

fernet: Fernet = Fernet(AUTH_CODE_SECRET)

if not RECAPTCHA_SECRET_KEY: raise ValueError("RECAPTCHA_SECRET_KEY not set in environment variables.")
google_verify_url: str = f"https://www.google.com/recaptcha/api/siteverify?secret={RECAPTCHA_SECRET_KEY}&response="

templates: Jinja2Templates = Jinja2Templates(directory="templates")

bearer_token_auth: BearerTokenAuth = BearerTokenAuth()

token_manager: TokenManager = TokenManager(
    access_token_expire_time=int(ACCESS_TOKEN_EXPIRE_MINUTES),
    refresh_token_expire_time=int(REFRESH_TOKEN_EXPIRE_MINUTES),
    private_key_path=str(JWT_PRIVATE_PEM_PATH),
    public_key_path=str(JWT_PUBLIC_PEM_PATH),
    token_algorithm=str(TOKEN_ALGORITHM)
)

db_manager: DBManager = DBManager(
    connection_string=get_connection_string(
        port=MONGO_PORT, 
        host=MONGO_HOST, 
        username=MONGO_ROOT_USERNAME, 
        password=MONGO_ROOT_PASSWORD), 
    db_name=MONGO_DATABASE_NAME)

db_manager.create_auth_service_client(
    AUTH_CLIENT_ID=AUTH_CLIENT_ID, 
    AUTH_CLIENT_SECRET=AUTH_CLIENT_SECRET, 
    AUTH_SERVICE_HOST=AUTH_SERVICE_HOST, 
    AUTH_SERVICE_PORT=AUTH_SERVICE_PORT
)
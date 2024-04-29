from fastapi import HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from database.db_manager import DBManager
from cryptography.fernet import Fernet
from models.account_models import Account
from models.scope_models import ProfileScope
from models.token_models import AccessToken, TokenType
from models.util_models import AuthenticatedAccount
from utils.scope_utils import str_to_list_of_profile_scopes
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

class BearerTokenAuth:
    """
    A class used to authenticate a user using a Bearer token.
    """
    token_prefix: str
    
    def __init__(self, token_prefix: str = "Bearer"):
        """
        The constructor for the BearerTokenAuth class.

        Args:
            token_prefix (str, optional): The prefix for the Bearer token. Defaults to "Bearer".
        """
        self.token_prefix = token_prefix
        
    def abstract_token_from_header(self, auth_header: str | None) -> str:
        """
        Abstracts the token from the Authorization header.

        Args:
            auth_header (str | None): The Authorization header as a string.

        Returns:
            str: The token as a string. None if the token is invalid or not present.
        """
        if not auth_header: return None
        split_auth_header: list[str] = auth_header.split(" ")
        if not len(split_auth_header) == 2: return None
        if not split_auth_header[0] == self.token_prefix: return None
        return split_auth_header[1]
    
    def raise_invalid_token_error(self) -> None:
        """
        Raises an HTTPException with status code 401 and a message indicating an invalid token.
        """
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail=f"Invalid {self.token_prefix} token")
    
    async def __call__(self, request: Request) -> AuthenticatedAccount:
        """
        Callable method to authenticate the user using the access Bearer token.
        Use as an endpoint parameter to obtain the account of the user assosiated with the token.

        Args:
            request (Request): Used to get the headers from the request.

        Returns:
            AuthenticatedAccount: The authenticated account object of the user associated with the token. Raises an HTTPException if the token is invalid.
        """
        auth_header = request.headers.get("Authorization")
        token: str = self.abstract_token_from_header(auth_header=auth_header)
        if not token: self.raise_invalid_token_error()
        decoded_token: AccessToken = token_manager.verify_and_decode_jwt_token(token=token, token_type=TokenType.ACCESS)
        if not decoded_token: self.raise_invalid_token_error()
        account: Account = db_manager.accounts_interface.get_account(username=decoded_token.sub)
        if not account: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            detail="Issue fetching account information")
        scopes: list[ProfileScope] = str_to_list_of_profile_scopes(scopes_str_list=decoded_token.scope)
        authenticated_account: AuthenticatedAccount = AuthenticatedAccount(**account.model_dump(), request_scopes=scopes)
        return authenticated_account
    
bearer_token_auth: BearerTokenAuth = BearerTokenAuth()
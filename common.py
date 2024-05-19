from fastapi import HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from config.config import Config
from database.db_manager import DBManager
from cryptography.fernet import Fernet
from models.account_models import Account
from models.token_models import AccessToken, TokenType
from models.util_models import AuthenticatedAccount
from utils.token_manager import TokenManager
from utils.database_utils import get_connection_string

config: Config = Config()

fernet: Fernet = Fernet(config.auth_config.authentication_code_secret)

google_verify_url: str = f"https://www.google.com/recaptcha/api/siteverify?secret={config.google_recaptcha_config.secret_key}&response="

templates: Jinja2Templates = Jinja2Templates(directory="templates")

token_manager: TokenManager = TokenManager(
    access_token_expire_time=int(config.jwt_config.access_token_expire),
    refresh_token_expire_time=int(config.jwt_config.refresh_token_expire),
    state_token_expire_time=int(config.jwt_config.state_token_expire),
    private_key_path=str(config.jwt_config.private_key_path),
    public_key_path=str(config.jwt_config.public_key_path),
    token_algorithm=str(config.jwt_config.token_algorithm.value)
)

db_manager: DBManager = DBManager(
    connection_string=get_connection_string(
        port=config.database_config.port, 
        host=config.database_config.host, 
        username=config.database_config.username, 
        password=config.database_config.password), 
    db_name=config.database_config.name)

# Load the default client model into the database if it does not exist
from services.client_services import load_client_model
if db_manager.clients_interface.get_client(client_id=config.default_client_config.client_id) is None:
    db_manager.clients_interface.add_client(client=load_client_model(client_id=config.default_client_config.client_id,
                                                                      client_secret=config.default_client_config.client_secret,
                                                                      redirect_port=config.api_config.port,
                                                                      redirect_host=config.api_config.host,
                                                                      client_model_path=config.default_client_config.client_model_path))

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
        if not verify_token_hash(token=decoded_token, token_type=TokenType.ACCESS):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
        account: Account = db_manager.accounts_interface.get_account(username=decoded_token.sub)
        if not account: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            detail="Issue fetching account information")
        authenticated_account: AuthenticatedAccount = AuthenticatedAccount(**account.model_dump(), access_token=decoded_token)
        return authenticated_account
    
from validators.auth_validators import verify_token_hash
bearer_token_auth: BearerTokenAuth = BearerTokenAuth()
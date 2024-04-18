from fastapi.security import OAuth2PasswordBearer
from security.models import AuthenticatedUser
from database.manager import DBManager
from security.password_manager import PasswordManager
from dotenv import load_dotenv
import os

load_dotenv(override=True)

TOKEN_ALGORITHM: str = os.getenv("TOKEN_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

class AuthenticationManager:
    oauth2_scheme: OAuth2PasswordBearer
    db_manager: DBManager
    
    def __init__(self,db_manager: DBManager  ,tokenUrl: str = "token") -> None:
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl=tokenUrl)
        self.db_manager = db_manager
        
    def authenticate_user(self, username: str, password: str) -> AuthenticatedUser:
        """
        Authenticates a user based on the username and password provided.

        Args:
            username (str): Username of user to be authenticated. Used to retrieve the hashed password from the database.
            password (str): Plain text password to be verified.

        Returns:
            AuthenticatedUser: AuthenticatedUser object if the user was authenticated successfully, None otherwise.
        """
        user: AuthenticatedUser | None = self.db_manager.users_interface.get_user(username=username)
        if not user: return None
        if not PasswordManager.verify_password(plain_password=password, hashed_password=user.hashed_password):
            return None
        return user
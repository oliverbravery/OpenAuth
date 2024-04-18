from pydantic import BaseModel
from enum import Enum

class TokenType(Enum):
    """
    TokenType Enum class for the token types.
    """
    ACCESS = "access"
    REFRESH = "refresh"
    
class TokenData(BaseModel):
    """
    Base TokenData model extending Pydantic's BaseModel class.
    """
    sub: str
    
    def dict(self, *args, **kwargs) -> dict:
        """
        Returns the dictionary representation of the TokenData object.

        Returns:
            dict: Dictionary representation of the TokenData object.
        """
        return {
            "sub": self.sub
        }

class User(BaseModel):
    """
    Base User model extending Pydantic's BaseModel class.
    """
    username: str

class AuthenticatedUser(User):
    """
    Authenticated User model extending the User model. Used in the authentication purposes.
    """
    hashed_password: str
    access_secret_key: str
    refresh_secret_key: str
    last_JWT_generation: str | None = None
    
    def dict(self, *args, **kwargs) -> dict:
        """
        Returns the dictionary representation of the AuthenticatedUser object.

        Returns:
            dict: Dictionary representation of the AuthenticatedUser object.
        """
        return {
            "username": self.username,
            "hashed_password": self.hashed_password,
            "access_secret_key": self.access_secret_key,
            "refresh_secret_key": self.refresh_secret_key,
            "last_JWT_generation": self.last_JWT_generation
        }
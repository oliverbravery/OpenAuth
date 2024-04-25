from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class TokenType(Enum):
    """
    Enum class for the token types.
    """
    ACCESS = "access"
    REFRESH = "refresh"
    
class BaseToken(BaseModel):
    """
    A class used to represent the base token data.
    Args:
        sub (str): The subject of the token. Usually the username of the user.
        aud (list[str]): The audience of the token. Usually the client_id of the application.
        exp (datetime): The expiration time of the token. Recommended to allow for clock skew.
        iat (datetime): The time the token was issued. Used to determine if the token is expired.
        iss (str, optional): The issuer of the token. Defaults to "auth-service".
        typ (str, optional): The type of the token. Defaults to "JWT".
    """
    iss: str = "auth-service"
    typ: str = "JWT"
    sub: str
    aud: list[str]
    exp: datetime
    iat: datetime
        
    def model_dump(self) -> dict:
        """
        Dumps the model into a dictionary, converting any datetime objects to their respective Unix timestamps.
        
        Returns:
            dict: The dictionary representation of the model.
        """
        return {
            "iss": self.iss,
            "typ": self.typ,
            "sub": self.sub,
            "aud": self.aud,
            "exp": self.exp.timestamp(),
            "iat": self.iat.timestamp()
        }
        
class AccessToken(BaseToken):
    """
    A class used to represent the access token data.
    Inherited from the BaseToken class.

    Args:
        sub (str): The subject of the token. Usually the username of the user.
        aud (list[str]): The audience of the token. Usually the client_id of the application.
        exp (datetime): The expiration time of the token. Recommended to allow for clock skew.
        iat (datetime): The time the token was issued. Used to determine if the token is expired.
        scope (list[str]): The list of scopes allowed by the token.
        iss (str, optional): The issuer of the token. Defaults to "auth-service".
        typ (str, optional): The type of the token. Defaults to "JWT".
    """
    scope: list[str]
        
    def model_dump(self) -> dict:
        """
        Dumps the model into a dictionary, converting any datetime objects to their respective Unix timestamps.
        
        Returns:
            dict: The dictionary representation of the model.
        """
        return {
            **super().model_dump(),
            "scope": self.scope
        }
        
class RefreshToken(BaseToken):
    """
    A class used to represent the refresh token data.
    Inherited from the BaseToken class.
    """
    pass
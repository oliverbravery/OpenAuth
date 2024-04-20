from datetime import timedelta
import datetime
from jose import jwt
from routes.authentication.models import TokenType, AccessToken

class TokenManager:
    """
    TokenManager class is responsible for managing the JWT tokens (access and refresh tokens).
    It provides methods for creating tokens and getting the expire time for the tokens.
    """
    access_token_expire_time: int
    refresh_token_expire_time: int
    token_algorithm: str
    secret_key: str
    
    def __init__(self, access_token_expire_time: int, refresh_token_expire_time: int, 
                 secret_key: str, token_algorithm: str = "RS256") -> None:
        """
        Initializes the TokenManager object.

        Args:
            access_token_expire_time (int): Time in minutes for the access token to expire.
            refresh_token_expire_time (int): Time in minutes for the refresh token to expire.
            secret_key (str): Secret key to be used for encoding the JWT token.
            token_algorithm (str, optional): Algorithm to be used for encoding the JWT token. Defaults to "RS256".
        """
        self.access_token_expire_time = access_token_expire_time
        self.refresh_token_expire_time = refresh_token_expire_time
        self.secret_key = secret_key
        self.token_algorithm = token_algorithm
        
    def get_token_expire_time(self, token_type: TokenType) -> int:
        """
        Gets the expire time for the token based on the token type.

        Args:
            token_type (TokenType): TokenType enum value for the token.

        Returns:
            int: Time in minutes for the token to expire.
        """
        match token_type:
            case TokenType.ACCESS:
                return self.access_token_expire_time
            case TokenType.REFRESH:
                return self.refresh_token_expire_time
            
    def calculate_jwt_timestamps(self, token_type: TokenType) -> tuple[datetime.datetime, datetime.datetime]:
        """
        Calculates the iat and exp timestamps for the JWT token.

        Args:
            token_type (TokenType): The type of token for which the timestamps are calculated.

        Returns:
            tuple[datetime.datetime, datetime.datetime]: Tuple containing the iat and the exp for the token (iat, exp).
        """
        current_time: datetime.datetime = datetime.datetime.now(datetime.UTC)
        expire: datetime.datetime = current_time + timedelta(minutes=self.get_token_expire_time(token_type=token_type))
        return current_time, expire
    
    def sign_jwt_token(self, token: AccessToken) -> dict:
        """
        Signs the JWT token using the provided data and token type.

        Args:
            token (AccessToken): The data to be included in the JWT token.
            token_type (TokenType): The type of token to be signed.

        Returns:
            dict: The signed JWT token.
        """
        to_encode: dict = token.model_dump()
        encoded_jwt: str = jwt.encode(to_encode, self.secret_key, algorithm=self.token_algorithm)
        return encoded_jwt
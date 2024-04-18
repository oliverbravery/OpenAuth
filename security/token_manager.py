from datetime import datetime, timedelta
from security.models import TokenType, TokenData
from jose import jwt

class TokenManager:
    access_token_expire_time: int
    refresh_token_expire_time: int
    token_algorithm: str
    
    def __init__(self, access_token_expire_time: int, refresh_token_expire_time: int, 
                 token_algorithm: str = "HS256") -> None:
        """
        Initializes the TokenManager object.

        Args:
            access_token_expire_time (int): Time in minutes for the access token to expire.
            refresh_token_expire_time (int): Time in minutes for the refresh token to expire.
            token_algorithm (str, optional): Algorithm to be used for encoding the JWT token. Defaults to "HS256".
        """
        self.access_token_expire_time = access_token_expire_time
        self.refresh_token_expire_time = refresh_token_expire_time
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
    
    def create_token(self, data: TokenData, token_type: TokenType, secret_key: str) -> str:
        """
        Creates a JWT token based on the data, token type and secret key.

        Args:
            data (TokenData): TokenData object containing the data to be encoded in the token.
            token_type (TokenType): TokenType enum value for the token. Allows to set different expire times for different token types.
            secret_key (str): Secret key to be used for encoding the token.

        Returns:
            str: Encoded JWT token.
        """
        to_encode: dict = data.dict().copy()
        current_time: datetime = datetime.now(datetime.UTC)
        expire: datetime = current_time + timedelta(minutes=self.get_token_expire_time(token_type))
        to_encode.update({"exp": expire})
        to_encode.update({"iat": current_time})
        encoded_jwt: str = jwt.encode(to_encode, secret_key, algorithm=self.token_algorithm)
        return encoded_jwt
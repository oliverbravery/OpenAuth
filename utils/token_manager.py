from base64 import urlsafe_b64encode
from datetime import timedelta
import datetime
import jwt
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
from models.account_models import Account
from models.token_models import AccessToken, BaseToken, RefreshToken, TokenType

class TokenManager:
    """
    TokenManager class is responsible for managing the JWT tokens (access and refresh tokens).
    It provides methods for creating tokens and getting the expire time for the tokens.
    """
    access_token_expire_time: int
    refresh_token_expire_time: int
    token_algorithm: str
    private_key: PrivateKeyTypes
    public_key: PublicKeyTypes
    
    def __init__(self, access_token_expire_time: int, refresh_token_expire_time: int, 
                 private_key_path: str, public_key_path: str, token_algorithm: str = "RS256") -> None:
        """
        Initializes the TokenManager object.

        Args:
            access_token_expire_time (int): Time in minutes for the access token to expire.
            refresh_token_expire_time (int): Time in minutes for the refresh token to expire.
            private_key_path (str): The path to the private key file.
            public_key_path (str): The path to the public key file.
            token_algorithm (str, optional): Algorithm to be used for encoding the JWT token. Defaults to "RS256".
        """
        self.access_token_expire_time = access_token_expire_time
        self.refresh_token_expire_time = refresh_token_expire_time
        self.private_key = self.__load_pem_key(key_path=private_key_path, is_public=False)
        self.public_key = self.__load_pem_key(key_path=public_key_path, is_public=True)
        self.token_algorithm = token_algorithm
        
    def __load_pem_key(self, key_path: str, is_public: bool) -> PublicKeyTypes | PrivateKeyTypes:
        """
        Loads the PEM encoded key from the provided path.

        Args:
            key_path (str): The path to the key file.
            is_public (bool): True if the key is public, False if the key is private.

        Returns:
            PublicKeyTypes | PrivateKeyTypes: The key object
        """
        key = None
        with open(key_path, "rb") as key_file:
            if is_public:
                key = load_pem_public_key(
                    data=key_file.read(),
                )
            else:
                key = load_pem_private_key(
                    key_file.read(),
                    password=None,
                )
        return key
            
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
    
    def sign_jwt_token(self, token: BaseToken) -> str:
        """
        Signs the JWT token using the provided data.

        Args:
            token (BaseToken): The data to be included in the JWT token.

        Returns:
            str: The signed string interpretation of the JWT token.
        """
        to_encode: dict = token.model_dump()
        encoded_jwt: str = jwt.encode(to_encode, self.private_key, algorithm=self.token_algorithm)
        return encoded_jwt
    
    def decode_jwt_token(self, token: str, token_type: TokenType) -> BaseToken:
        """
        Decodes the JWT token using the provided data.
        Checks the token was signed with the correct secret key.

        Args:
            token (str): The JWT token to be decoded.
            token_type (TokenType): The type of token to be decoded.

        Returns:
            BaseToken: The decoded token object. None if the token is invalid.
        """
        token_class: BaseToken
        match token_type:
            case TokenType.ACCESS:
                token_class = AccessToken
            case TokenType.REFRESH:
                token_class = RefreshToken
        try:
            decoded_jwt_token: dict[str, any] = jwt.decode(token, self.public_key, algorithms=[self.token_algorithm], options={"verify_aud": False})
        except Exception as e:
            return None
        return token_class(**decoded_jwt_token)
    
    @staticmethod
    def verify_token_not_expired(token: BaseToken) -> bool:
        """
        Verifies that the token has not expired.

        Args:
            token (BaseToken): The token to be verified.

        Returns:
            bool: True if the token has not expired, False otherwise.
        """
        current_time: datetime.datetime = datetime.datetime.now(datetime.UTC)
        return current_time < token.exp and current_time > token.iat 
    
    def verify_and_decode_jwt_token(self, token: str, token_type: TokenType) -> BaseToken:
        """
        Verifies and decodes the JWT token using the provided data.
        Checks the token was signed with the correct secret key and has not expired.

        Args:
            token (str): The JWT token to be decoded.
            token_type (TokenType): The type of token to be decoded.

        Returns:
            BaseToken: The decoded token object. None if the token is invalid or has expired.
        """
        decoded_token: BaseToken = self.decode_jwt_token(token=token, token_type=token_type)
        if not decoded_token or not TokenManager.verify_token_not_expired(token=decoded_token):
            return None
        return decoded_token
    
    def generate_and_sign_jwt_token(self, tokenType: TokenType, account: Account, client_id: str, scopes: str) -> str:
        """
        Generates a JWT token for the given account and token type.

        Args:
            tokenType (TokenType): The type of token to be generated.
            account (Account): The account for which the token is generated.
            client_id: (str): The requesting application's client_id.
            scopes (str): The scopes for the token (space separated string of scopes).

        Returns:
            str: The generated and signed JWT token.
        """
        iat, exp = self.calculate_jwt_timestamps(token_type=tokenType)
        token: BaseToken
        match tokenType:
            case TokenType.ACCESS:
                if scopes is None: scopes = ""
                token: AccessToken = AccessToken(
                    sub=account.username,
                    aud=client_id,
                    exp=exp,
                    iat=iat,
                    scope=scopes
                )
            case TokenType.REFRESH:
                token: RefreshToken = RefreshToken(
                    sub=account.username,
                    aud=client_id,
                    exp=exp,
                    iat=iat,
                )
        return self.sign_jwt_token(token=token)
    
    def generate_jwks_dict(self) -> dict:
        """
        Generates the JWKS dictionary for the API.

        Returns:
            dict: The JWKS dictionary for the API.
        """
        public_numbers = self.public_key.public_numbers()
        jwk: dict[str, any] = {
            "kty": "RSA",
            "n": urlsafe_b64encode(public_numbers.n.to_bytes(
                (public_numbers.n.bit_length() + 7) // 8, byteorder="big")).decode("utf-8").rstrip("="),
            "e": urlsafe_b64encode(public_numbers.e.to_bytes(
                (public_numbers.e.bit_length() + 7) // 8, byteorder="big")).decode("utf-8").rstrip("="),
        }
        return jwk
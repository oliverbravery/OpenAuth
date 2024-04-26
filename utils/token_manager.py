from datetime import timedelta
import datetime
from jose import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from models.account_models import Account, Profile
from models.token_models import AccessToken, BaseToken, RefreshToken, TokenType
from utils.account_utils import get_profile_from_account
from utils.scope_utils import profile_scope_list_to_str

class TokenManager:
    """
    TokenManager class is responsible for managing the JWT tokens (access and refresh tokens).
    It provides methods for creating tokens and getting the expire time for the tokens.
    """
    access_token_expire_time: int
    refresh_token_expire_time: int
    token_algorithm: str
    private_key: bytes # PEM encoded private key
    
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
        self.private_key = self.__load_pem_key(key_path=private_key_path)
        self.token_algorithm = token_algorithm
        
    def __load_pem_key(self, key_path: str) -> str:
        """
        Loads the PEM encoded key from the provided path.

        Args:
            key_path (str): The path to the key file.

        Returns:
            str: The PEM encoded key.
        """
        with open(key_path, "rb") as key_file:
            private_key = load_pem_private_key(
                key_file.read(),
                password=None,  # Provide a password if the key is encrypted
            )
            private_key_str = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ).decode("utf-8")
            return private_key_str
            
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
        #TODO: RS256 needs PEM encoded private key to sign the token. This is asymetric so need to generate PEM public and private key. Sign with private, give public to clients to verify that tokens are legit.
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
            decoded_jwt_token: dict[str, any] = jwt.decode(token, self.public_key, algorithms=[self.token_algorithm])
        except jwt.JWTError:
            return None
        return token_class(**decoded_jwt_token)
    
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
        if not decoded_token or not self.verify_token_not_expired(decoded_token):
            return None
        return decoded_token
    
    def generate_and_sign_jwt_token(self, tokenType: TokenType, account: Account, client_id: str) -> str:
        """
        Generates a JWT token for the given account and token type.

        Args:
            tokenType (TokenType): The type of token to be generated.
            account (Account): The account for which the token is generated.
            client_id: (str): The requesting application's client_id.

        Returns:
            str: The generated and signed JWT token.
        """
        iat, exp = self.calculate_jwt_timestamps(token_type=tokenType)
        token: BaseToken
        match tokenType:
            case TokenType.ACCESS:
                profile: Profile = get_profile_from_account(account=account,
                                                            client_id=client_id)
                if not profile: return None
                token: AccessToken = AccessToken(
                    sub=account.username,
                    aud=[client_id],
                    exp=exp,
                    iat=iat,
                    scope=profile_scope_list_to_str(profile_scopes=profile.scopes)
                )
            case TokenType.REFRESH:
                token: RefreshToken = RefreshToken(
                    sub=account.username,
                    aud=[client_id],
                    exp=exp,
                    iat=iat,
                )
        return self.sign_jwt_token(token=token)
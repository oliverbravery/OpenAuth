from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ResponseType(str, Enum):
    """
    Enum class for the response types.
    """
    CODE = "code"

class AuthorizationRequest(BaseModel):
    """
    A class used to represent the data required to authorize a user following the OAuth2.0 protocol.
    It is used to parse the data from the request body when authorizing a user.
    
    Args:
        client_id (str): The id of the application. Used to know which application is requesting access.
        client_secret (str): The secret of the application. Used to authenticate the application.
        scope str: The list of requested scopes as a space-separated string.
        response_type (ResponseType): The type of response. Should be 'code' for the authorization code flow.
        state (str): A random string generated by the client. Used to prevent CSRF attacks. Returned in the response.
        code_challenge (str): The code challenge generated by the client. Used by PKCE to prevent code interception attacks.
    """
    client_id: str
    client_secret: str
    response_type: ResponseType
    state: str
    code_challenge: str
    scope: str
        
class GrantType(str, Enum):
    """
    Enum class for the grant types.
    """
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"
        
class TokenRequest(BaseModel):
    """
    A class used to represent the data required to exchange an authorization code for an access token following the OAuth2.0 protocol.
    It is used to parse the data from the request body when exchanging an authorization code for an access token.
    
    Args:
        grant_type (GrantType): The type of grant. Should be 'authorization_code' for the authorization code flow.
        client_id (str): The id of the application. Used to know which application is requesting access.
        client_secret (str): The secret of the application. Used to authenticate the application.
        code (str): The authorization code generated by the auth service.
        code_verifier (str): The code verifier generated by the client. Used by PKCE to prevent code interception attacks.
        refresh_token (str, optional): Optional. The refresh token generated by the auth service. Used to get a new access token.
    """
    grant_type: GrantType
    client_id: str
    client_secret: str
    code: str
    code_verifier: str
    refresh_token: Optional[str]
    
    def model_dump(self) -> dict:
        return {
            "grant_type": self.grant_type.value,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": self.code,
            "code_verifier": self.code_verifier,
            "refresh_token": self.refresh_token
        }
        
class UpdateAccountRequest(BaseModel):
    username: str
    attribute_updates: Dict[str, Any]
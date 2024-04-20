from fastapi.param_functions import Form
from pydantic import BaseModel
from enum import Enum

class TokenType(Enum, str):
    """
    Enum class for the token types.
    """
    ACCESS = "access"
    REFRESH = "refresh"

class GrantType(Enum, str):
    """
    Enum class for the grant types.
    """
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"
    
class ResponseType(Enum, str):
    """
    Enum class for the response types.
    """
    CODE = "code"
        
class AuthorizationForm:
    """
    A class used to represent the data required to authorize a user following the OAuth2.0 protocol.
    It is used to parse the data from the request body when authorizing a user.
    """
    def __init__(
        self,
        username: str = Form(),
        password: str = Form(),
        client_id: str = Form(),
        client_secret: str = Form(), 
        scope: list[str] = Form(), 
        response_type: ResponseType = Form(),
        state: str = Form(),
        code_challenge: str = Form(),
    ):
        """
        The constructor for the AuthorizationForm class.
        
        Args:
            username (str): The username of the user.
            password (str): The plaintext password of the user.
            client_id (str): The id of the application. Used to know which application is requesting access.
            client_secret (str, optional): Optional. The secret of the application. Used to authenticate the application.
            scope (list[str]): The list of requested scopes.
            response_type (ResponseType): The type of response. Should be 'code' for the authorization code flow.
            state (str): A random string generated by the client. Used to prevent CSRF attacks. Returned in the response.
            code_challenge (str): The code challenge generated by the client. Used by PKCE to prevent code interception attacks.
        """
        self.username: str = username
        self.password: str = password
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.scope: list[str] = scope
        self.response_type: ResponseType = response_type
        self.state: str = state
        self.code_challenge: str = code_challenge
        
class TokenForm:
    """
    A class used to represent the data required to exchange an authorization code for an access token following the OAuth2.0 protocol.
    It is used to parse the data from the request body when exchanging an authorization code for an access token.
    """
    def __init__(
        self,
        grant_type: GrantType = Form(),
        client_id: str = Form(),
        code: str = Form(),
        code_verifier: str = Form(),
        refresh_token: str = Form(None),
    ):
        """
        The constructor for the TokenForm class.
        
        Args:
            grant_type (GrantType): The type of grant. Should be 'authorization_code' for the authorization code flow.
            client_id (str): The id of the application. Used to know which application is requesting access.
            code (str): The authorization code generated by the auth service.
            code_verifier (str): The code verifier generated by the client. Used by PKCE to prevent code interception attacks.
            refresh_token (str, optional): Optional. The refresh token generated by the auth service. Used to get a new access token.
        """
        self.grant_type: GrantType = grant_type
        self.client_id: str = client_id
        self.code: str = code
        self.code_verifier: str = code_verifier
        self.refresh_token: str = refresh_token
        
class AuthorizeResponse(BaseModel):
    """
    A class used to represent the response data when authorizing a user following the OAuth2.0 protocol.
    """
    def __init__(
        self,
        authorization_code: str,
        state: str,
    ):
        """
        The constructor for the AuthorizeResponse class.
        
        Args:
            authorization_code (str): The authorization code generated by the auth service.
            state (str): The state generated by the client. Used to prevent CSRF attacks.
        """
        self.authorization_code: str = authorization_code
        self.state: str = state
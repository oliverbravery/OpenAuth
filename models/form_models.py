from typing import Any, Dict, List
from fastapi.param_functions import Form
from pydantic import BaseModel, Field
from models.client_models import ClientDeveloper, MetadataAttribute
from models.request_models import AuthorizationRequest
from models.scope_models import ClientScope

class UserRegistrationForm:
    """
    A class used to represent a new account form. 
    It is used to parse the data from the request body when registering a new account.
    """
    def __init__(
        self,
        username: str = Form(),
        password: str = Form(),
        email: str = Form(),
        display_name: str = Form(),
    ):
        self.username: str = username
        self.password: str = password
        self.email: str = email
        self.display_name: str = display_name
        
class LoginForm(AuthorizationRequest):
    """
    A class used to represent the data required to authenticate a user.
    It is used to parse the data from the request body when authenticating a user.
    """
    username: str = Form()
    password: str = Form()
    totp_pin: str = Form()
    g_recaptcha_response: str = Form(alias="g-recaptcha-response")
    
class ConsentForm(AuthorizationRequest):
    """
    A class used to represent the data required to get user consent following the OAuth2.0 protocol.
    It is used to parse the data from the request body when getting user consent.
    """
    client_redirect_uri: str
    consented: str
    username: str
    
class ClientRegistrationForm(BaseModel):
    """
    A class used to represent a new client form. 
    It is used to parse the data from the request body when registering a new client.
    """
    client_name: str = Field(..., description="The name of the client to register.", max_length=100)
    client_description: str = Field(..., description="A description of the client used in the consent page.", max_length=2000)
    client_redirect_uri: str = Field(..., description="The URI to which the user is redirected after granting or denying access to the client.")
    client_developers: List[ClientDeveloper] = Field(..., description="The developers that have access to the client along with the scopes they have access to.")
    client_scopes: List[ClientScope] = Field(..., description="The client specific scopes and what attributes each scope can control.")
    client_profile_metadata_attributes: List[MetadataAttribute] = Field(..., description="The metadata attributes that the client can store in the user's profile.")
    client_profile_defaults: Dict[str, Any] = Field(..., description="The default values for the metadata attributes that the client can store in the user's profile.")
from fastapi.param_functions import Form

from models.request_models import AuthorizationRequest

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
    
class ConcentForm(AuthorizationRequest):
    """
    A class used to represent the data required to get user consent following the OAuth2.0 protocol.
    It is used to parse the data from the request body when getting user consent.
    """
    client_redirect_uri: str
    consented: str
    username: str
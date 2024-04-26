from enum import Enum
from pydantic import BaseModel

from models.client_models import ClientScope

class DBCollection(Enum):
    """
    Enum class for the database collections
    """
    AUTHORIZATION = "authorization"
    ACCOUNTS = "accounts"
    CLIENTS = "clients"
    
class Endpoints(str, Enum):
    """
    Enum class for the authorization endpoints.
    """
    AUTHORIZE = "/authentication/authorization"
    LOGIN = "/authentication/login"
    CONSENT = "/authentication/consent"
    
class ConcentDetails(BaseModel):
    """
    A class used to represent the data required to display the consent page.
    
    Args:
        name (str): The name of the client application.
        description (str): The description of the client application / the scopes requested.
        requested_scopes (list[ClientScope]): The description of the scopes requested.
        client_redirect_uri (str): The redirect uri of the client application.
    """
    name: str
    description: str
    requested_scopes: list[ClientScope]
    client_redirect_uri: str
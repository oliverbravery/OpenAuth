from enum import Enum
from pydantic import BaseModel

from models.account_models import Account
from models.scope_models import ClientScope, ProfileScope

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
    
class ClientCredentialType(Enum):
    """
    Enum class for the client credential types mapped to their byte length.
    """
    ID = 16
    SECRET = 32
    
class ConsentDetails(BaseModel):
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
    
class AuthenticatedAccount(Account):
    """
    Represents an authenticated account. 
    
    Derived from the Account class with additional request scopes.

    Args:
        Account (Account): The account object for the authenticated account.
        request_scopes (list[ProfileScope]): The scopes found in the verified bearer token.
    """
    request_scopes: list[ProfileScope]
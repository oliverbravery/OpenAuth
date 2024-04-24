from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Dict
from typing import Optional
from fastapi.param_functions import Form
from pydantic import BaseModel, field_validator
from enum import Enum
from datetime import datetime

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
        scopes_description (dict[str, str]): The description of the scopes requested. Key is the scope name, value is the scope description.
        client_redirect_uri (str): The redirect uri of the client application.
    """
    name: str
    description: str
    scopes_description: dict[str, str]
    client_redirect_uri: str
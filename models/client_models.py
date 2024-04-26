from enum import Enum
from typing import List, Dict, Any

from pydantic import BaseModel

from models.scope_models import ClientScope, DeveloperScope

class ClientDeveloper(BaseModel):
    """
    Represents what scopes a developer has access to for a client.
    
    Args:
        username (str): The unique username of the developer.
        scopes (List[DeveloperScope]): The scopes that the developer has access to for the client.
    """
    username: str
    scopes: List[DeveloperScope]
    
class MetadataType(Enum):
    """
    Represents the possible types for a metadata attribute.
    """
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    
class MetadataAttribute(BaseModel):
    """
    Represents a metadata attribute for a client.
    
    Args:
        name (str): The name of the metadata attribute.
        description (str): The description of the metadata attribute.
        type (MetadataType): The type of the metadata attribute.
    """
    name: str
    description: str
    type: MetadataType

class Client(BaseModel):
    """
    Represents a registered application in the auth service. 
    A client is an application that can request access to a user's account and store application-specific data in the user's profile.
    
    Args:
        client_id (str): The unique attribute used to identify and differentiate applications.
        client_secret (str): A long random string that is used to authenticate the application.
        name (str): The name of the application.
        description (str): A description of the application and why it needs access to certain scopes.
        redirect_uri (str): The URI to which the user is redirected after granting or denying access to the application.
        developers (List[ClientAdmin]): The list of developers that have access to the client.
        scopes (list[ClientScope]): The scopes of the client.
        profile_metadata_attributes (List[MetadataAttribute]): The metadata attributes that the client can store in the user's profile.
        profile_defaults (dict[str, any]): Any default values that the client wants to store in the user's profile.
    """
    client_id: str
    client_secret: str
    name: str
    description: str
    redirect_uri: str
    developers: List[ClientDeveloper] = []
    scopes: list[ClientScope] = []
    profile_metadata_attributes: list[MetadataAttribute] = []
    profile_defaults: Dict[str, Any] = {}
    
    def get_profile_default(self, key: str) -> any:
        """
        Get the default value for the given key.

        Args:
            key (str): The key of the default value.

        Returns:
            any: The default value for the given key. None if the key does not exist.
        """
        return self.profile_defaults.get(key, None)